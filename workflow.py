from agents import run_single_pass
def run_workflow_for_product(product: dict) -> dict:
    state = {
        "product": product,  # Store dict directly, NO re-indexing
        "research": {},
        "strategy": {},
        "draft": {},
        "review": {},
    }
    state = run_single_pass(state)
    return state

