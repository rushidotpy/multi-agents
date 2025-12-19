from typing import Any, Dict
from agents import run_single_pass

def run_workflow_for_product(product: Dict[str, Any]) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "product": product,   # product dict directly here
        "research": {},
        "strategy": {},
        "draft": {},
        "review": {},
    }
    state = run_single_pass(state)
    return state
