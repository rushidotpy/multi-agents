import streamlit as st
from data_loader import load_products
from workflow import run_workflow_for_product

# 1) Load preset products from products.json
products = load_products()

st.title("Multi-Agent Marketing Brief Automator")

# 2) UI inputs (PUT YOUR LINE HERE)
col1, col2 = st.columns(2)
with col1:
    preset_id = st.selectbox(
        "Quick demos:",
        [""] + list(products.keys())
    )
with col2:
    custom_prompt = st.text_input("Or describe your product:")

# 3) Run workflow when button is clicked  
if st.button("Run Workflow"):
    if preset_id:  # preset_id = "ai_coding_tutor"
        product = products[preset_id]  # ← GET FULL DICT
    else:
        product = {
            "product_name": custom_prompt or "Custom Product",
            "short_description": custom_prompt or "",
            "target_audience": "general",
            "goals": ["drive awareness"],
            "constraints": {"tone": "professional", "word_count_limit": 1200}
        }
    state = run_workflow_for_product(product)  # Now passes DICT

    st.subheader("Review")
    st.write(f"Approved: {state['review']['approved']}")
    st.write(f"Issues: {state['review']['issues']}")
    st.write(state["review"]["comments"])

    st.subheader("Key Messages")
    for msg in state["strategy"]["key_messages"]:
        st.write(f"- {msg}")

    st.subheader("Draft Brief")
    st.markdown(state["draft"]["text"])
