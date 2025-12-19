import json
import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products.json")

def load_products(path: str = PRODUCTS_PATH) -> Dict[str, Any]:
<<<<<<< HEAD
    print("Loading products from:", path)  # will appear in Streamlit logs
=======
>>>>>>> 090c8034595fdd4c1eeade7307a4b21d9f3c5058
    with open(path, "r") as f:
        products = json.load(f)
    return {p["product_id"]: p for p in products}
