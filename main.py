import streamlit as st
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
import asyncio
from chat_utils import generate_rag_response,streamchat
from file_utils import generate_document
from query_engine import get_query_engine_from_text

load_dotenv()

async def main():
    st.title("Infi Book AI")
    uploaded_files = st.file_uploader("Upload File",
                                      accept_multiple_files=True,
                                      type=["pdf"],
                                      key="general_agent")

    if uploaded_files:
        print("Inside uploaded files")
        all_text = ""
        for uploaded_file in uploaded_files:
            all_text += extract_text(uploaded_file) + "\n\n"
        
        query_engine = get_query_engine_from_text(all_text, top_k=7)
        st.session_state.query_engine = query_engine

    text_area = st.text_area("Provide sub chapters seperated by | ")
    textsplit = ""
    if text_area is not None:
        textsplit = text_area.split("|")

    generated_documents = []

    if st.button('Generate documents'):
        print("Generate documents called")
        num_columns = len(textsplit)
        columns = st.columns(num_columns)
        tasks = []

        for idx, (text, col) in enumerate(zip(textsplit, columns), start=1):
            output_placeholder = col.empty()
            # Add each streamchat task to our list
            tasks.append(streamchat(output_placeholder, text.strip()))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

            # download_link = generate_document(response, idx)
            # generated_documents.append(download_link)
            
            
    # for document in generated_documents:
    #     st.markdown(document, unsafe_allow_html=True)


if __name__ == "__main__":
    asyncio.run(main())
