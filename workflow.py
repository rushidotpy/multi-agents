from typing import Any, Dict
from agents import run_single_pass

def run_workflow_for_product(product: Dict[str, Any], run_reviewer: bool) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "product": product,
        "research": {},
        "strategy": {},
        "draft": {},
        "review": {},
    }
    state = run_single_pass(state, run_reviewer=run_reviewer)
    return state
