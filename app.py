import streamlit as st
from data_loader import load_products
from workflow import run_workflow_for_product

st.title("Multi-Agent Marketing Brief Automator")

products = load_products()
product_ids = list(products.keys())
choice = st.selectbox("Choose a product", product_ids)

if st.button("Run workflow"):
    with st.spinner("Running multi-agent workflow..."):
        state = run_workflow_for_product(choice)

    st.subheader("Review")
    st.write("Approved:", state["review"]["approved"])
    st.write("Issues:", state["review"]["issues"])
    st.write(state["review"]["comments"])

    st.subheader("Key Messages")
    for msg in state["draft"]["key_messages"]:
        st.write("- ", msg)

    st.subheader("Draft Brief")
    st.text_area("Draft", state["draft"]["text"], height=400)
