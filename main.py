import streamlit as st
from dotenv import load_dotenv
import asyncio
from chat_utils import streamchat
from pdfminer.high_level import extract_text
from query_engine import get_all_ids, get_query_engine_from_text, reset_collection

load_dotenv()

st.set_page_config(layout="wide")

async def main():
    st.title("Infi Book AI")

    # Sidebar for input controls
    with st.sidebar:
        st.header("Input Section")
        uploaded_files = st.file_uploader("Upload File",
                                          accept_multiple_files=True,
                                          type=["pdf"],
                                          key="general_agent")
        
        text_area = st.text_area("Provide sub chapters separated by |")
        textsplit = text_area.split("|") if text_area else []

        if st.button("Clear memory"):
            reset_collection()

        generate_button = st.button('Generate documents')

    # Main area for content
    main_content = st.empty()

    if generate_button:
        if uploaded_files:
            all_text = ""
            for uploaded_file in uploaded_files:
                all_text += extract_text(uploaded_file) + "\n\n"

            query_engine = get_query_engine_from_text(all_text, top_k=7)
            st.session_state.query_engine = query_engine
        
        main_content.write("Generating documents...")
        await generate_documents(textsplit, main_content)

async def generate_documents(textsplit, main_content):
    num_columns = len(textsplit)
    if num_columns == 0:
        main_content.write("No sub-chapters provided. Please enter sub-chapters separated by | in the sidebar.")
        return

    column_width = 1 / num_columns
    columns = main_content.columns(num_columns * [column_width])
    tasks = []

    for idx, (text, col) in enumerate(zip(textsplit, columns), start=1):
        output_placeholder = col.empty()
        tasks.append(streamchat(output_placeholder, text.strip(), idx))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())