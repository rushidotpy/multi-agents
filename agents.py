from typing import Dict, List, Any
from tools import web_search
from llm_client import call_llm
import time

# ---------- Types ----------

AgentState = Dict[str, Any]  # shared state dict passed between agents

# ---------- Researcher ----------
def researcher_agent(state):
    product = state["product"]
    product_name = product["product_name"]
    short_description = product["short_description"]
    target_audience = product["target_audience"]
    goals = product["goals"]
    constraints = product["constraints"]
    
    system_prompt = (
    "You are a market researcher. From the product info, return 3–5 customer pains, "
    "3–5 benefits, and up to 3 competitor insights in sections titled 'Customer pains', "
    "'Benefits', and 'Competitors'. Limit: 120 words total."
)


    
    user_content = f"""
Research this product for marketing:
- Name: {product_name}
- Description: {short_description}
- Audience: {target_audience}
- Goals: {', '.join(goals)}
"""
    
    raw_snippets = call_llm(system_prompt, user_content)
    
    import json
    try:
        snippets = json.loads(raw_snippets)
    except:
        snippets = []
    
    state["research"] = {
        "snippets": snippets[:8],
        "timestamp": "now"
    }
    return state


# ---------- Strategist ----------

def strategist_agent(state: AgentState) -> AgentState:
    product = state["product"]
    research = state["research"]
    system_prompt = (
    "You are a marketing strategist. Using the research, return target audience (1–2 sentences), "
    "positioning (≤2 sentences), 3–5 key messages, and tone/style (1–2 sentences), with headings. "
    "Limit: 200 words."
)



    snippets_text = "\n\n".join(
        f"- {s['title']}: {s['snippet']}" for s in research["snippets"][:8]
    )

    user_content = f"""
Product:
- Name: {product['product_name']}
- Description: {product['short_description']}
- Target audience: {product['target_audience']}
- Goals: {', '.join(product.get('goals', []))}
- Constraints: {product.get('constraints', {})}

Research snippets:
{snippets_text}
"""

    raw = call_llm(system_prompt, user_content)

    import json
    try:
        parsed = json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        parsed = json.loads(raw[start : end + 1])

    outline = parsed.get("outline", [])
    key_messages = parsed.get("key_messages", [])

    state["strategy"] = {
        "outline": outline,
        "key_messages": key_messages,
        "research_used": research["snippets"][:5],
    }
    
    return state

# ---------- Writer ----------
def writer_agent(state: AgentState) -> AgentState:
    product = state["product"]
    strategy = state["strategy"]
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

Outline:
{chr(10).join(strategy['outline'])}

Key messages:
{chr(10).join('- ' + m for m in strategy['key_messages'])}
{review_notes}
"""

    draft_text = call_llm(system_prompt, user_content)

    state["draft"] = {
        "text": draft_text,
        "key_messages": strategy["key_messages"],
    }

    return state

# ---------- Reviewer ----------

def reviewer_agent(state: AgentState) -> AgentState:
    draft = state["draft"]
    product = state["product"]

    system_prompt = (
    "You are an editor. Review the draft for clarity, structure, tone, and fit with the product spec; "
    "return a bullet list of issues and specific fixes or short rewrites only. "
    "Do not rewrite the whole article. Limit: 200 words."
)



    user_content = f"""
Product:
- Name: {product['product_name']}
- Description: {product['short_description']}
- Target audience: {product['target_audience']}
- Goals: {', '.join(product.get('goals', []))}
- Constraints: {product.get('constraints', {})}

Draft brief:
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

def run_single_pass(state: AgentState) -> AgentState:
    # 1) Research + strategy once
    print("Starting researcher")
    state = researcher_agent(state)
    time.sleep(1)
    print("Starting strategist")
    state = strategist_agent(state)
    time.sleep(1)
    # 2) Writer + Reviewer loop
    max_rounds = 3
    for round_idx in range(max_rounds):
        print("Starting writer")
        state = writer_agent(state)
        time.sleep(1)
        print("Starting reviewer")
        state = reviewer_agent(state)
        time.sleep(1)

        if state["review"].get("approved"):
            # Approved – stop looping
            state["review"]["rounds"] = round_idx + 1
            print("Finished single pass")
            return state

        # Not approved – add a note for the next round
        # (the writer_agent already reads product + strategy; you can also
        #  modify it later to incorporate review['issues'] if you want)
        state["review"]["rounds"] = round_idx + 1

    # 3) If still not approved after max_rounds, return best effort
    return state
