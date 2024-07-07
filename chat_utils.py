import os
import re
import asyncio

from constants import OPENAI_MODEL,CLAUDE_MODEL
from llm_provider import LLMProvider
from anthropic import Anthropic
import streamlit as st
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

from constants import BOOK_GENERATOR
from file_utils import generate_document,generate_download_link

openai_api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY")

openai_llm_async = AsyncOpenAI(api_key=openai_api_key)
claude_llm_async = Anthropic(api_key=claude_api_key)


async def streamchat(placeholder,query,index,llm_provider=LLMProvider.OPENAI.value):
    if "query_engine" not in st.session_state:
        return "Sorry no document found"

    chunks = st.session_state.query_engine.query(query)

    context_str = "\n\n".join(chunk.get("content") for chunk in chunks)
    prompt = BOOK_GENERATOR.format(
        query=query,context=context_str
    )
    system_message = "You are an advanced AI assistant. You are helpful, informative, and friendly. Your responses should be engaging, polite, and clear. Provide accurate information and clarify any ambiguities. If you don't know the answer to a question, say so honestly. Maintain a neutral tone and do not express personal opinions. Assist users with their questions and provide explanations where necessary."
    streamed_text = ""

    if llm_provider == LLMProvider.OPENAI.value:
        if not openai_api_key:
             placeholder.info("Sorry , openai api key is not set.")
             return
        stream_coroutine  = openai_llm_async.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            temperature=0.7,
            top_p=1
        )
        stream = await stream_coroutine
        
        async for chunk in stream:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                streamed_text = streamed_text + chunk_content
                placeholder.info(streamed_text)
    elif llm_provider == LLMProvider.CLAUDE.value:
        if not claude_api_key:
             placeholder.info("Sorry , claude api key is not set.")
             return
        with claude_llm_async.messages.stream(
            max_tokens=4096,
            messages=[
                {"role": "user", "content": system_message+prompt}
            ],
            model=CLAUDE_MODEL,
        ) as stream:
            for text in stream.text_stream:
                streamed_text += text
                placeholder.info(streamed_text)
                await asyncio.sleep(0)
    else:
        placeholder.info("Invalid model choice. Please choose 'openai' or 'claude'.")


    title,streamed_text_without_title  = extract_title(streamed_text) or f"Document {index}"
    doc_bytes = generate_document(streamed_text_without_title, index,title)
    download_link = generate_download_link(streamed_text_without_title,title)
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
                {streamed_text_without_title}
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
        title = match.group(2).strip()
        text = re.sub(r'^\s*##?\s*.+\n?', '', text, count=1, flags=re.MULTILINE)
        return title, text

    # If no match found, try to find the first non-empty line
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            return line.strip(), '\n'.join(lines[i+1:])

    return None, text