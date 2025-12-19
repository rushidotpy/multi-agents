import json
import streamlit as st
from data_loader import load_products
from workflow import run_workflow_for_product
from llm_client import call_llm

products = load_products()

st.title("Multi-Agent Marketing Brief Automator")

col1, col2 = st.columns(2)
with col1:
    preset_id = st.selectbox(
        "Quick demos:",
        [""] + list(products.keys())
    )
with col2:
    custom_prompt = st.text_input("Or describe your product:")

run_reviewer = st.checkbox("Run reviewer step", value=True)

if st.button("Run Workflow"):
    if preset_id:
        product = products[preset_id]
    else:
        prompt = (custom_prompt or "").strip()
        if not prompt:
            st.error("Please choose a preset or describe your product.")
            st.stop()

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
                "wealth_band": spec.get("wealth_band", "not specified"),
            },
        }

    with st.spinner("Running multi-agent workflow..."):
        state = run_workflow_for_product(product, run_reviewer=run_reviewer)

    st.subheader("Draft")
    st.markdown(state["draft"]["text"])

    if run_reviewer and state.get("review"):
        st.subheader("Review")
        st.write(f"Approved: {state['review']['approved']}")
        st.write(f"Issues: {state['review']['issues']}")
        st.write(state["review"]["comments"])
