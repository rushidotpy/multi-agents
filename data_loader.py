import json
from typing import Dict, Any

def load_products(path: str = "data/knowledge/products.json") -> Dict[str, Any]:
    with open(path, "r") as f:
        products = json.load(f)
    # index by product_id for easy access
    return {p["product_id"]: p for p in products}
