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
    unique_sources = get_unique_sources(chunks)

    context_str = "\n\n".join(chunk.get("content") for chunk in chunks)

    prompt = BOOK_GENERATOR.format(
        query=query,context=context_str
    )
    system_message = "You are an advanced AI assistant. You are helpful, informative, and friendly. Your responses should be engaging, polite, and clear. Provide accurate information and clarify any ambiguities. If you don't know the answer to a question, say so honestly. Maintain a neutral tone and do not express personal opinions. Assist users with their questions and provide explanations where necessary."
    streamed_text = ""

    try:
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
                temperature=0.7
            ) as stream:
                for text in stream.text_stream:
                    streamed_text += text
                    placeholder.info(streamed_text)
                    await asyncio.sleep(0)
        else:
            placeholder.info("Invalid model choice. Please choose 'openai' or 'claude'.")
    except Exception as e:
        print("Error in getting output :",e)
        placeholder.info(f"Unable to get answer from LLM Provider : {llm_provider} ")



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
        .source-chip {
            display: inline-block;
            padding: 0 12px;
            height: 24px;
            font-size: 12px;
            line-height: 24px;
            border-radius: 12px;
            background-color: rgba(25, 118, 210, 0.8);  
            color: white;
            margin: 5px 5px 5px 0;
            border: 1px solid rgba(25, 118, 210, 1);
        }
        .download-link-container a {
            display: inline-block;
            padding: 8px 16px;
            background-color: #2196F3;
            color: white !important;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }

        .download-link-container a:hover {
            background-color: #1976D2;
            text-decoration: none;
        }
        /* Theme-specific styles */
        @media (prefers-color-scheme: dark) {
            .chat-container {
                background-color: rgba(61, 157, 243, 0.3); 
            }
            .chat-index {
                color: rgba(255, 255, 255, 0.7);
            }
           .source-chip {
                background-color: rgba(144, 202, 249, 0.8);  
                color: #06166a; 
                border-color: rgba(144, 202, 249, 1);
            }
            .download-link-container a {
                background-color: #64B5F6;
                color: #0d47a1 !important;
            }
            .download-link-container a:hover {
                background-color: #90CAF9;
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
                <div class="download-link-container">
                    {download_link}
                </div>
                <div class="source-list">
                {''.join([f'<span class="source-chip">{source}</span>' for source in unique_sources])}
                </div>
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

def get_unique_sources(chunks):
    unique_filenames = set()
    
    for chunk in chunks:
        if 'metadata' in chunk:
            unique_filenames.add(chunk.get("metadata").get("filename",""))
    
    return list(unique_filenames)