import streamlit as st
from dotenv import load_dotenv

import asyncio
from chat_utils import streamchat
from file_uploader import upload_files

load_dotenv()

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
