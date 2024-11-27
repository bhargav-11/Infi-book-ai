__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import zipfile
import io
import streamlit as st
from dotenv import load_dotenv
import asyncio
from constants import CLAUDE_DEFAULT_SETTINGS, OPENAI_DEFAULT_SETTINGS
from file_extension import FileExtension
from chat_utils import streamchat
from pdfminer.high_level import extract_text
from file_utils import extract_doc_text, extract_docx_text
from query_engine import get_documents_from_text, get_query_engine_from_text, reset_collection
from load_keys import load_keys
from sidebar import render_sidebar

load_dotenv()

st.set_page_config(layout="wide")

async def main():

    if 'keys_loaded' not in st.session_state:
        st.session_state.keys_loaded = False
    
    if not st.session_state.keys_loaded:
        load_keys()
        st.session_state.keys_loaded = True

    if 'all_documents' not in st.session_state:
        st.session_state.all_documents = {}

    if "generated_responses" not in st.session_state:
        st.session_state.generated_responses = {}

    if "openai_config" not in st.session_state:
        st.session_state.openai_config = OPENAI_DEFAULT_SETTINGS
    if "claude_config" not in st.session_state:
        st.session_state.claude_config = CLAUDE_DEFAULT_SETTINGS
           

    st.title("Infi Book AI")

    # Sidebar for input controls
    uploaded_files, textsplit, generate_button, download_button_placeholder = render_sidebar()

    # Main area for content
    main_content = st.empty()
    if generate_button:
        if uploaded_files:
            reset_collection()
            
            st.session_state.all_documents = {}
            st.session_state.generated_responses ={}
            documents = []
            index=1
            for uploaded_file in uploaded_files:
                if uploaded_file.type == FileExtension.PDF.value:
                    text= extract_text(uploaded_file)
                    documents_from_pdf = get_documents_from_text(text,uploaded_file.name,index)
                    documents.extend(documents_from_pdf) 
                    index+= len(documents_from_pdf)
                elif uploaded_file.type == FileExtension.DOCX.value:
                    text= extract_docx_text(uploaded_file)
                    documents_from_docx = get_documents_from_text(text,uploaded_file.name,index)
                    documents.extend(documents_from_docx)
                    index += len(documents_from_docx)
                elif uploaded_file.type == FileExtension.DOC.value:
                    text=extract_doc_text(uploaded_file)
                    documents_from_doc= get_documents_from_text(text,uploaded_file.name,index)
                    documents.extend(documents_from_doc)
                    index+=len(documents_from_doc)

            query_engine = get_query_engine_from_text(documents, top_k=7)
            st.session_state.query_engine = query_engine
        
        main_content.write("Generating documents...")
        await generate_documents(textsplit, main_content)
    
    if "all_documents" in st.session_state and st.session_state.all_documents:
        zip_buffer = create_zip_file()
        download_button_placeholder.download_button(
            label="Download all documents",
            data=zip_buffer,
            file_name="all_documents.zip",
            mime="application/zip"
        )
    else:
        download_button_placeholder.download_button(
            label="Download all documents",
            data="a",
            disabled=True
        )

async def generate_documents(textsplit, main_content):
    
    if not textsplit:
        main_content.write("No sub-chapters provided. Please enter sub-chapters separated by | in the sidebar.")
        return

    # Create a fixed number of columns

    num_fixed_columns = len(textsplit)
    if len(textsplit) > 3:
        num_fixed_columns = 3
    columns = main_content.columns(num_fixed_columns)

    tasks = []

    for idx, text in enumerate(textsplit, start=1):
        # Use modulo to cycle through the fixed columns
        col = columns[(idx-1) % num_fixed_columns]
        output_placeholder = col.empty()
        tasks.append(streamchat(output_placeholder, text.strip(), idx,st.session_state.llm_provider))

    await asyncio.gather(*tasks)

def create_zip_file():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in st.session_state.all_documents.items():
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer


if __name__ == "__main__":
    asyncio.run(main())