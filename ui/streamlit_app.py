# ui/streamlit_app.py
import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("MoSPI RAG Chatbot (demo)")
q = st.text_input("Ask a question from the scraped corpus")
k = st.slider("k (top chunks)", 1, 10, 4)
if st.button("Ask"):
    with st.spinner("Querying..."):
        resp = requests.post(f"{API_URL}/ask", json={"question": q, "k": k})
        if resp.status_code == 200:
            data = resp.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("Citations")
            for c in data["citations"]:
                st.markdown(f"- {c['title']} — `{c['url']}`")
        else:
            st.error(resp.text)
