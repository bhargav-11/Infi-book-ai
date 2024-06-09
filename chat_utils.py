import os

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from constants import short_book_generator_prompt, short_book_prompt

openai_api_key = os.environ.get("OPENAI_API_KEY")

langchain_openai_client = ChatOpenAI(api_key=openai_api_key,
                                     model="gpt-4o",
                                     verbose=True)


def generate_rag_response(query):
    """
  Generate a response using the RAG pipeline.

  Args:
      query (str): The query to generate a response using qa_chain.

  Returns:
      str: The generated response.
  """
    if "retriever" not in st.session_state:
        return "Sorry no document found"

    prompt_template = ChatPromptTemplate.from_template(short_book_prompt)

    retriever = st.session_state.retriever
    rag_chain = ({
        "context": retriever,
        "subtopic_summary": RunnablePassthrough()
    }
                 | prompt_template
                 | langchain_openai_client
                 | StrOutputParser())
    response = rag_chain.invoke(query)
    return response
