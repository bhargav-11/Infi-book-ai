import streamlit as st
from dotenv import load_dotenv

import asyncio
from chat_utils import streamchat
from pdfminer.high_level import extract_text
from query_engine import get_query_engine_from_text

load_dotenv()

async def main():
    st.title("Infi Book AI")
    uploaded_files = st.file_uploader("Upload File",
                                      accept_multiple_files=True,
                                      type=["pdf"],
                                      key="general_agent")
    
    text_area = st.text_area("Provide sub chapters seperated by | ")
    textsplit = ""
    if text_area is not None:
        textsplit = text_area.split("|")

    if st.button('Generate documents'):
        if uploaded_files:
            all_text = ""
            for uploaded_file in uploaded_files:
                all_text += extract_text(uploaded_file) + "\n\n"

            query_engine = get_query_engine_from_text(all_text, top_k=7)
            st.session_state.query_engine = query_engine
        print("Generate documents called")
        num_columns = len(textsplit)
        columns = st.columns(num_columns)
        tasks = []

        for idx, (text, col) in enumerate(zip(textsplit, columns), start=1):
            output_placeholder = col.empty()
            # Add each streamchat task to our list
            tasks.append(streamchat(output_placeholder, text.strip(),idx))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)            

if __name__ == "__main__":
    asyncio.run(main())
