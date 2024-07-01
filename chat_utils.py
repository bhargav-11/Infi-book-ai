import os

import streamlit as st
from llama_index.llms.openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

from constants import BOOK_GENERATOR
from file_utils import generate_document

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_key=openai_api_key, model="gpt-4o")
llm_async = AsyncOpenAI(api_key=openai_api_key)

def generate_rag_response(query):
    """
  Generate a response using the RAG pipeline.

  Args:
      query (str): The query to generate a response using qa_chain.

  Returns:
      str: The generated response.
  """
    if "query_engine" not in st.session_state:
        return "Sorry no document found"

    chunks = st.session_state.query_engine.query(query)
    context_str = "\n\n".join(chunk.get("content") for chunk in chunks)
    prompt = BOOK_GENERATOR.format(
        query=query,context=context_str
    )
    response=chat(prompt)
    return response


def chat(prompt):
    response = llm.complete(prompt)
    return response.text


async def streamchat(placeholder,query,index):
    if "query_engine" not in st.session_state:
        return "Sorry no document found"

    chunks = st.session_state.query_engine.query(query)

    context_str = "\n\n".join(chunk.get("content") for chunk in chunks)
    prompt = BOOK_GENERATOR.format(
        query=query,context=context_str
    )
    stream_coroutine  = llm_async.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        temperature=0.4,
    )
    stream = await stream_coroutine
    streamed_text = " "
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            placeholder.info(streamed_text)

    download_link,doc_bytes = generate_document(streamed_text, index)
    st.session_state.all_documents[f"generated_document_{index}.docx"] = doc_bytes
    placeholder.markdown(
        f'''
        <div style="background-color: rgba(61, 157, 243, 0.2); padding: 10px; border-radius: 5px; color: rgb(199, 235, 255); margin-bottom: 20px;">
            <div style="font-size: 0.8em; color: rgba(199, 235, 255, 0.7); margin-bottom: 10px;">#{index}</div>
            <div style="margin-top: 10px;">
                {streamed_text}
                <br><br>
                {download_link}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )