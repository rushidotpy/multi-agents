from typing import Any, Dict
from data_loader import load_products
from agents import run_single_pass

def run_workflow_for_product(product_id: str) -> Dict[str, Any]:
    products = load_products()
    product = products[product_id]
    state = run_single_pass(product)
    return state

if __name__ == "__main__":
    state = run_workflow_for_product("ai_coding_tutor")
    print("Approved:", state["review"]["approved"])
    print("Issues:", state["review"]["issues"])
    print("Draft preview:\n", state["draft"]["text"][:800])
