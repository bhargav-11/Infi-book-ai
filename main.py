import streamlit as st
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

from chat_utils import generate_rag_response
from file_utils import generate_document
from query_engine import get_query_engine_from_text

load_dotenv()

def main():
    st.title("Infi Book AI")
    uploaded_files = st.file_uploader("Upload File",
                                      accept_multiple_files=True,
                                      type=["pdf"],
                                      key="general_agent")

    if uploaded_files:
        print("Inside uploaded files")
        for uploaded_file in uploaded_files:
            text = extract_text(uploaded_file)
            query_engine = get_query_engine_from_text(text, top_k=7)

            if "query_engine" not in st.session_state:
                st.session_state.query_engine = query_engine

    text_area = st.text_area("Provide sub chapters seperated by | ")
    textsplit = ""
    if text_area is not None:
        textsplit = text_area.split("|")

    generated_documents = []

    if st.button('Generate documents'):
        print("Generate documents called")
        for idx, text in enumerate(textsplit, start=1):
            response = generate_rag_response(text)

            download_link = generate_document(response, idx)
            generated_documents.append(download_link)
            
            
    for document in generated_documents:
        st.markdown(document, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
