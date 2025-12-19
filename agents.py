from typing import Dict, List, Any
from llm_client import call_llm
import time

AgentState = Dict[str, Any]  # shared state dict passed between agents

# ---------- Researcher ----------

def researcher_agent(state: AgentState) -> AgentState:
    product = state["product"]
    product_name = product["product_name"]
    short_description = product["short_description"]
    target_audience = product["target_audience"]
    goals = product["goals"]

    system_prompt = (
        "You are a market researcher. From the product info, return 3–5 customer pains, "
        "3–5 benefits, and up to 3 competitor insights in sections titled 'Customer pains', "
        "'Benefits', and 'Competitors'. Limit: 120 words total."
    )

    # Only minimal product info, no extra fields
    user_content = f"""
Research this product for marketing:
- Name: {product_name}
- Description: {short_description}
- Audience: {target_audience}
- Goals: {', '.join(goals)}
"""

    raw = call_llm(system_prompt, user_content)

    # Here we just store the raw text (already short) instead of forcing JSON
    state["research"] = {
        "summary": raw,
        "timestamp": "now",
    }
    return state

# ---------- Strategist ----------

def strategist_agent(state: AgentState) -> AgentState:
    product = state["product"]
    research = state["research"]["summary"]

    system_prompt = (
        "You are a marketing strategist. Using the product info and research, "
    "return concrete content, not questions.\n"
    "Output:\n"
    "- Target audience: 1–2 sentences describing who this is for.\n"
    "- Positioning: ≤2 sentences clearly describing the value.\n"
    "- 3–5 key messages as short bullet points.\n"
    "- Tone & style: 1–2 sentences.\n"
    "Do not ask for more information. Limit: 200 words."
    )

    user_content = f"""
Product:
- Name: {product['product_name']}
- Description: {product['short_description']}
- Target audience: {product['target_audience']}
- Goals: {', '.join(product.get('goals', []))}

Research:
{research}
"""

    raw = call_llm(system_prompt, user_content)

    # Expect a simple structured text, not heavy JSON
    state["strategy"] = {
        "text": raw
    }
    return state

# ---------- Writer ----------

def writer_agent(state: AgentState) -> AgentState:
    product = state["product"]
    strategy_text = state["strategy"]["text"]
    previous_review = state.get("review")  # may be None

    review_notes = ""
    if previous_review and not previous_review.get("approved", True):
        issues = previous_review.get("issues", [])
        if issues:
            review_notes = "\n\nReviewer feedback to address:\n- " + "\n- ".join(issues)

    system_prompt = (
        "You are a marketing copywriter. Write a blog post with title, intro, 3–5 headed sections, "
        "and conclusion based on the product and strategy. Style: clear, persuasive, skimmable. "
        "Limit: 800–1,000 words."
    )

    user_content = f"""
Product:
- Name: {product['product_name']}
- Description: {product['short_description']}
- Target audience: {product['target_audience']}
- Goals: {', '.join(product.get('goals', []))}
- Constraints: {product.get('constraints', {})}

Strategy:
{strategy_text}
{review_notes}
"""

    draft_text = call_llm(system_prompt, user_content)

    state["draft"] = {
        "text": draft_text,
    }
    return state

# ---------- Reviewer (optional) ----------

def reviewer_agent(state: AgentState) -> AgentState:
    draft = state["draft"]
    product = state["product"]

    system_prompt = (
        "You are an editor. Review the draft for clarity, structure, tone, and fit with the product spec; "
        "return JSON with fields: approved (bool), issues (list of short strings), comments (string). "
        "Do not rewrite the whole article. Limit: 200 words."
    )

    user_content = f"""
Product:
- Name: {product['product_name']}
- Description: {product['short_description']}
- Target audience: {product['target_audience']}
- Goals: {', '.join(product.get('goals', []))}
- Constraints: {product.get('constraints', {})}

Draft:
{draft['text']}
"""

    raw = call_llm(system_prompt, user_content)

    import json
    try:
        parsed = json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        parsed = json.loads(raw[start : end + 1])

    approved = bool(parsed.get("approved", False))
    issues = parsed.get("issues", [])
    comments = parsed.get("comments", "")

    state["review"] = {
        "approved": approved,
        "issues": issues,
        "comments": comments,
    }

    return state

# ---------- Orchestrator helper ----------

def run_single_pass(state: AgentState, run_reviewer: bool) -> AgentState:
    # 1) Research + strategy once
    print("Starting researcher")
    state = researcher_agent(state)
    time.sleep(0.5)

    print("Starting strategist")
    state = strategist_agent(state)
    time.sleep(0.5)

    # 2) Writer
    print("Starting writer")
    state = writer_agent(state)

    # 3) Optional reviewer loop
    if not run_reviewer:
        return state

    max_rounds = 2
    for round_idx in range(max_rounds):
        print("Starting reviewer")
        state = reviewer_agent(state)
        time.sleep(0.5)

        if state["review"].get("approved"):
            state["review"]["rounds"] = round_idx + 1
            return state

        # Not approved – let writer see issues next round
        print("Starting writer (revision)")
        state = writer_agent(state)
        time.sleep(0.5)

    # If still not approved after max_rounds, return best effort
    state["review"]["rounds"] = max_rounds
    return state
