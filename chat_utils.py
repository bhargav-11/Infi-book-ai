import os
import re
import streamlit as st
from llama_index.llms.openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

from constants import BOOK_GENERATOR
from file_utils import generate_document

openai_api_key = os.getenv("OPENAI_API_KEY")

# llm = OpenAI(api_key=openai_api_key, model="gpt-4o")
llm_async = AsyncOpenAI(api_key=openai_api_key)

# def generate_rag_response(query):
#     """
#   Generate a response using the RAG pipeline.

#   Args:
#       query (str): The query to generate a response using qa_chain.

#   Returns:
#       str: The generated response.
#   """
#     if "query_engine" not in st.session_state:
#         return "Sorry no document found"

#     chunks = st.session_state.query_engine.query(query)
#     context_str = "\n\n".join(chunk.get("content") for chunk in chunks)
#     prompt = BOOK_GENERATOR.format(
#         query=query,context=context_str
#     )
#     response=chat(prompt)
#     return response


# def chat(prompt):
#     response = llm.complete(prompt)
#     return response.text


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
            {"role": "system", "content": "You are an advanced AI assistant. You are helpful, informative, and friendly. Your responses should be engaging, polite, and clear. Provide accurate information and clarify any ambiguities. If you don't know the answer to a question, say so honestly. Maintain a neutral tone and do not express personal opinions. Assist users with their questions and provide explanations where necessary."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        temperature=0.7,
        top_p=1
    )
    stream = await stream_coroutine
    streamed_text = " "
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            placeholder.info(streamed_text)

    title = extract_title(streamed_text) or f"Document {index}"
    download_link,doc_bytes = generate_document(streamed_text, index,title)
    document_name = f"{title}.docx" if title else f"generated_document_{index}.docx"
    st.session_state.all_documents[document_name] = doc_bytes
    
    st.markdown("""
        <style>
        .chat-container {
            background-color: rgba(61, 157, 243, 0.2);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .chat-index {
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 10px;
        }
        .chat-content {
            margin-top: 5px;
        }
        /* Theme-specific styles */
        @media (prefers-color-scheme: dark) {
            .chat-container {
                background-color: rgba(61, 157, 243, 0.3);  /* Slightly more opaque for better visibility */
            }
            .chat-index {
                color: rgba(255, 255, 255, 0.7);
            }
        }
        @media (prefers-color-scheme: light) {
            .chat-container {
                background-color: rgba(61, 157, 243, 0.2);
            }
            .chat-index {
                color: rgba(0, 0, 0, 0.7);
            }
        }
        </style>
        """, unsafe_allow_html=True)

    placeholder.markdown(
        f'''
        <div class="chat-container">
            <div class="chat-index">#{index}</div>
            <div class="chat-content">
            <h2>{title} </h2>
                {streamed_text}
                <br><br>
                {download_link}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def extract_title(text):
    # Try to find a line starting with ## or #
    match = re.search(r'^\s*(##?\s*)(.+)$', text, re.MULTILINE)
    if match:
        return match.group(2).strip()

    # If no match found, try to find the first non-empty line
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            return line.strip()

    return None