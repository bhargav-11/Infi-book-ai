__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from dotenv import load_dotenv

import asyncio
from chat_utils import streamchat
from file_uploader import upload_files

load_dotenv()
st.set_page_config(layout="wide")

async def main():
    st.title("Infi Book AI")
    upload_files()
    text_area = st.text_area("Provide sub chapters seperated by | ")
    textsplit = ""
    if text_area is not None:
        textsplit = text_area.split("|")

    if st.button('Generate documents'):
        print("Generate documents called")
        num_columns = len(textsplit)
        # Calculate the width for each column
        column_width = 1 / num_columns
        # Pass the column_width to the st.beta_columns function
        columns = st.columns(num_columns * [column_width])
        tasks = []

        for idx, (text, col) in enumerate(zip(textsplit, columns), start=1):
            output_placeholder = col.empty()
            # Add each streamchat task to our list
            tasks.append(streamchat(output_placeholder, text.strip(),idx))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)
        

if __name__ == "__main__":
    asyncio.run(main())
