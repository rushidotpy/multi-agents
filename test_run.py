from workflow import run_workflow_for_product
from data_loader import load_products

if __name__ == "__main__":
    products = load_products()
    product = products["ai_coding_tutor"]  # or any other preset key

    state = run_workflow_for_product(product, run_reviewer=True)

    print("\n=== DRAFT ===\n")
    print(state["draft"]["text"])

    if state.get("review"):
        print("\n=== REVIEW ===\n")
        print("Approved:", state["review"]["approved"])
        print("Issues:", state["review"]["issues"])
        print("Comments:", state["review"]["comments"])

