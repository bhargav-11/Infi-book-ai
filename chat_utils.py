import random
import re
import asyncio

from constants import OPENAI_O1_MODELS, TOP_K ,ENCRYPTED_KEYS_FILE_PATH,ENCRYPTION_KEY
from llm_provider import LLMProvider
from anthropic import Anthropic
import streamlit as st
from openai import AsyncOpenAI
from config_manager import EncryptedConfigManager

from search import aggregate_search_results, identify_subqueries_for_search_and_retrieval

from constants import BOOK_GENERATOR_V2
from file_utils import generate_document,generate_download_link




async def streamchat(placeholder,query,index,llm_provider=LLMProvider.OPENAI.value):
    try:
        search_queries, retrieval_subqueries =await identify_subqueries_for_search_and_retrieval(query)
    except Exception as e:
        print(f"Error in identifying subqueries: {e}")
        search_queries = []
        retrieval_subqueries = []
    
    try:
        chunks = st.session_state.query_engine.query(query)
        if retrieval_subqueries:
            for subquery in retrieval_subqueries:
                chunks.extend(st.session_state.query_engine.query(subquery))
    except Exception as e:
        print("No query engine found")
        chunks = []
        
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)

    openai_llm_async = AsyncOpenAI(api_key=config_manager.get_key("OPENAI_API_KEY"))
    claude_llm_async = Anthropic(api_key=config_manager.get_key("CLAUDE_API_KEY"))

    sorted_chunks = process_chunks(chunks,TOP_K)
    unique_sources = get_unique_sources(sorted_chunks)
    context_str = "\n\n".join(chunk.get("content") for chunk in sorted_chunks)
    if search_queries:
        search_queries_result = await aggregate_search_results(search_queries)
        search_results = "\n\n".join(f"Search Query: {result['query']}\nAnswer: {result['answer']}" for result in search_queries_result)
        prompt = BOOK_GENERATOR_V2.format( query=query,context=context_str,search_results=search_results)
        
        source_links = get_random_source_links(search_queries_result)
    else:
         prompt = BOOK_GENERATOR_V2.format( query=query,context=context_str,search_results="None")
         source_links= []

    system_message = f"""
    "You are an advanced AI assistant. You are helpful, informative, and friendly. 
    You are an AI capable of generating extremely detailed and comprehensive responses. 
    Your goal is to provide the most thorough and extensive information possible, without any regard for length constraints. 
    Continue expanding on each point until you've exhausted all relevant details
    Do not provide conclusion section.
    """    
    streamed_text = ""

    try:
        if llm_provider == LLMProvider.OPENAI.value:
            openai_config = st.session_state.openai_config
            finish_reason = ""
            if not config_manager.get_key("OPENAI_API_KEY"):
                placeholder.info("Sorry , openai api key is not set.")
                return
            
            print(openai_config)

            if openai_config["model"] in OPENAI_O1_MODELS:
                
                stream_coroutine  = openai_llm_async.chat.completions.create(
                    model=openai_config["model"],
                    messages=[
                        {"role": "user", "content": system_message + prompt},
                    ],
                    stream=True,
                    temperature=openai_config["temperature"],
                    top_p=openai_config["top_p"],
                    presence_penalty=openai_config["presence_penalty"],
                    frequency_penalty=openai_config["frequency_penalty"]
                )
            else:
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ]
                stream_coroutine  = openai_llm_async.chat.completions.create(
                    model=openai_config["model"],
                    messages=messages,
                    stream=True,
                    temperature=openai_config["temperature"],
                    max_tokens=openai_config["max_tokens"],
                    top_p=openai_config["top_p"],
                    presence_penalty=openai_config["presence_penalty"],
                    frequency_penalty=openai_config["frequency_penalty"]
                )

            
            stream = await stream_coroutine
            
            async for chunk in stream:
                chunk_content = chunk.choices[0].delta.content
                finish_reason= chunk.choices[0].finish_reason
                if chunk_content is not None:
                    streamed_text = streamed_text + chunk_content
                    placeholder.info(streamed_text)

            if finish_reason == "length":
                if openai_config["model"] in OPENAI_O1_MODELS:
                    stream_coroutine  = openai_llm_async.chat.completions.create(
                        model=openai_config["model"],
                        messages=[
                            {"role":"user", "content":prompt},
                            {"role":"assistant","content":streamed_text},
                            {"role":"user", "content":"Continue "}
                        ],
                        stream=True,
                        temperature=openai_config["temperature"],
                        top_p=openai_config["top_p"],
                        presence_penalty=openai_config["presence_penalty"],
                        frequency_penalty=openai_config["frequency_penalty"]
                    )
                else:
                    stream_coroutine  = openai_llm_async.chat.completions.create(
                        model=openai_config["model"],
                        messages=[
                           {"role": "system", "content": system_message},
                           {"role": "user", "content": prompt},
                           {"role":"assistant","content":streamed_text},
                           {"role":"user", "content":"Continue "}  
                        ],
                        stream=True,
                        max_tokens=openai_config["max_tokens"],
                        temperature=openai_config["temperature"],
                        top_p=openai_config["top_p"],
                        presence_penalty=openai_config["presence_penalty"],
                        frequency_penalty=openai_config["frequency_penalty"]
                    )
                
                stream = await stream_coroutine

                async for chunk in stream:
                    chunk_content = chunk.choices[0].delta.content
                    finish_reason= chunk.choices[0].finish_reason
                    if chunk_content is not None:
                        streamed_text = streamed_text + chunk_content
                        placeholder.info(streamed_text)
                

        elif llm_provider == LLMProvider.CLAUDE.value:
            claude_config = st.session_state.claude_config
    
            if not config_manager.get_key("CLAUDE_API_KEY"):
                placeholder.info("Sorry , claude api key is not set.")
                return
            with claude_llm_async.messages.stream(
                messages=[
                    {"role": "user", "content": system_message+prompt}
                ],
                model=claude_config["model"],
                temperature=claude_config["temperature"],
                max_tokens=claude_config["max_tokens"],
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
                    {''.join([f'<span class="source-chip">{source}</span>' for source in unique_sources if source]) or '<span class="no-sources">No document sources available</span>'}
                </div>
                <div class="source-list">
                    {''.join([f'<span class="source-chip"><a href="{source}" target="_blank">Link {i+1}</a></span>' for i, source in enumerate(source_links) if source]) or '<span class="no-sources">No source/url links available</span>'}
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

def get_random_source_links(source_results):
    links= []
    for result in source_results:
        links.extend(result['sources'])
    unique_sources = list(set(links))
    source_links = random.sample(unique_sources, min(len(unique_sources), 6))
    return source_links

def process_chunks(chunks, max_chunks_size):
    unique_chunks = {}
    for chunk in chunks:
        unique_chunks[chunk['id']] = chunk
    
    unique_chunks_list = list(unique_chunks.values())
    
    sorted_chunks = sorted(unique_chunks_list, key=lambda x: x['score'], reverse=True)
    
    return sorted_chunks[:max_chunks_size]