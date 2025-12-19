import json
import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products.json")

def load_products(path: str = PRODUCTS_PATH) -> Dict[str, Any]:
    with open(path, "r") as f:
        products = json.load(f)
    return {p["product_id"]: p for p in products}
