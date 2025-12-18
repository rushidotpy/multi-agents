import json
from pathlib import Path

from agents import run_single_pass  # your agents.py

DATA_PATH = Path("data/products.json")

def load_first_product():
    with DATA_PATH.open() as f:
        products = json.load(f)
    return products[0]  # take first product

if __name__ == "__main__":
    product = load_first_product()
    state = run_single_pass(product)
    # Print final artifacts
    print("=== PRODUCT ===")
    print(product)
    print("\n=== REVIEW ===")
    print(state["review"])
    print("\n=== DRAFT (first 500 chars) ===")
    print(state["draft"]["text"][:500])
