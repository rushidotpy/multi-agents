from typing import Dict, List, Any
from tools import web_search
from llm_client import call_llm


# ---------- Types ----------

AgentState = Dict[str, Any]  # shared state dict passed between agents

# ---------- Researcher ----------
def researcher_agent(state):
    product = state["product"]["product"]
    product_name = product["product_name"]
    short_description = product["short_description"]
    target_audience = product["target_audience"]
    goals = product["goals"]
    constraints = product["constraints"]
    
    system_prompt = (
        "You are a market researcher. Find 5-8 relevant web snippets about "
        f"{product_name} and its {target_audience} audience. "
        "Respond as JSON list of snippets with 'title' and 'snippet' keys."
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
    product = state["product"]["product"]
    research = state["research"]

    system_prompt = (
        "You are a senior marketing strategist. "
        "Given a product and research snippets, design a structured marketing brief outline "
        "and 3–6 key messages. Respond in strict JSON with keys: "
        "outline (list of strings), key_messages (list of strings). "
        "Do not include any text outside the JSON."
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
    product = state["product"]["product"]
    strategy = state["strategy"]

    system_prompt = (
        "You are a marketing copywriter. "
        "Expand the outline into a full marketing brief. "
        "Respect tone, channels, and word count constraints when provided. "
        "Return plain markdown text only, no JSON."
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
    product = state["product"]["product"]

    system_prompt = (
        "You are a strict marketing reviewer. "
        "Given a product and a draft brief, decide if it is READY or NEEDS_CHANGES. "
        "Check: product fit, clarity, presence of key value prop, audience fit, and tone. "
        "Respond in strict JSON with keys: "
        "approved (true/false), issues (list of strings), comments (string). "
        "Do not include any text outside the JSON."
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

def run_single_pass(product: Dict[str, Any]) -> AgentState:
    """
    Simple one-shot pipeline:
    product -> Researcher -> Strategist -> Writer -> Reviewer
    This is *not* the full LangGraph/CrewAI orchestration,
    just a convenient function for testing agents in sequence.
    """
    state: AgentState = {"product": product}

    state = researcher_agent(state)
    state = strategist_agent(state)
    state = writer_agent(state)
    state = reviewer_agent(state)

    
    return state
