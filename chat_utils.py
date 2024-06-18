import os

import streamlit as st
from llama_index.llms.openai import OpenAI

from constants import SHORT_BOOk_GENERATOR

openai_api_key = os.environ.get("OPENAI_API_KEY")

llm = OpenAI(api_key=openai_api_key, model="gpt-4o")


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