import streamlit as st
from data_loader import load_products
from workflow import run_workflow_for_product
from llm_client import call_llm   
# 1) Load preset products from products.json
products = load_products()

st.title("Multi-Agent Marketing Brief Automator")

# 2) UI inputs
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
    if preset_id:
        product = products[preset_id]
    else:
        prompt = (custom_prompt or "").strip()
        if not prompt:
            st.error("Please choose a preset or describe your product.")
            st.stop()

        # 1) Ask LLM to summarize spec fields from the free-text prompt
        system_prompt = (
            "You are a marketing strategist. "
            "Given a product description, return JSON with fields: "
            "{"
            "  \"target_audience\": \"...\","
            "  \"wealth_band\": \"...\""
            "}. "
            "Keep it concise. Do not add any other fields or text."
        )
        spec_json = call_llm(system_prompt, prompt)
        # Assume call_llm returns a JSON string; parse it:
        import json
        try:
            spec = json.loads(spec_json)
        except Exception:
            spec = {"target_audience": "general audience", "wealth_band": "not specified"}

        product = {
            "product_name": prompt,
            "short_description": prompt,
            "target_audience": spec.get("target_audience", "general audience"),
            "goals": ["drive awareness"],
            "constraints": {
                "tone": "professional",
                "word_count_limit": 1200,
                # you can also pass wealth_band if your agents use it
                "wealth_band": spec.get("wealth_band", "not specified"),
            },
        }

    state = run_workflow_for_product(product)
