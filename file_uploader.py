import streamlit as st
from pdfminer.high_level import extract_text
from query_engine import get_query_engine_from_text

def upload_files():
    uploaded_files = st.file_uploader("Upload File",
                                      accept_multiple_files=True,
                                      type=["pdf"],
                                      key="general_agent")

    if uploaded_files:
        all_text = ""
        for uploaded_file in uploaded_files:
            all_text += extract_text(uploaded_file) + "\n\n"

        query_engine = get_query_engine_from_text(all_text, top_k=12)
        st.session_state.query_engine = query_engine