import os

import asyncio
import streamlit as st
from llama_index.llms.openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

from constants import SHORT_BOOk_GENERATOR

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
    prompt = SHORT_BOOk_GENERATOR.format(
        subtopic_summary=query,context=context_str
    )

    response = chat(prompt)
    return response


def chat(prompt):
    response = llm.complete(prompt)
    return response.text


async def streamchat(placeholder,query):
    if "query_engine" not in st.session_state:
        return "Sorry no document found"

    chunks = st.session_state.query_engine.query(query)

    context_str = "\n\n".join(chunk.get("content") for chunk in chunks)
    prompt = SHORT_BOOk_GENERATOR.format(
        subtopic_summary=query,context=context_str
    )
    stream_coroutine  = llm_async.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )
    stream = await stream_coroutine
    streamed_text = "# "
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            placeholder.info(streamed_text)
