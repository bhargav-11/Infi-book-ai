import json
import streamlit as st
from constants import RETRIEVAL_ONLY_PROMPT, SEARCH_AND_RETRIEVAL_PROMPT
from openai import OpenAI
from tavily import TavilyClient
from constants import ENCRYPTED_KEYS_FILE_PATH,ENCRYPTION_KEY
from config_manager import EncryptedConfigManager
import asyncio

async def get_answer(query,context):
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)
    prompt = (
      "You are an AI assistant specialized in answers to query using the provided context."
      "Please make sure to provide answer from the provided context"
      f"Query: {query}\n\n"
      f"Context: {context}\n\n"
      "Answer:"
    )
    client = OpenAI(api_key=config_manager.get_key("OPENAI_API_KEY"))
    response = await asyncio.to_thread(client.chat.completions.create,
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}])
    response_content = response.choices[0].message.content
    return response_content


async def get_query_context(query):
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)
    tavily_client = TavilyClient(api_key=config_manager.get_key("TAVILY_API_KEY"))

    response = await asyncio.to_thread(
                tavily_client.search,
                query,
                search_depth='advanced',
                use_cache=True
            )
    results = response.get("results", [])
    context = "\n\n".join([source["content"][:500] for source in results])
    sources = [result["url"] for result in results]
    return context,sources

async def get_search_answer(query):
    context,sources = await get_query_context(query)
    answer = await get_answer(query,context)
    return answer,sources


def convert_to_json(response):
    json_start = response.find("{")
    json_end = response.rfind("}") + 1
    json_str = response[json_start:json_end]

    # Parse the JSON string
    response_json = json.loads(json_str)
    return response_json

async def identify_subqueries_for_search_and_retrieval(user_query):
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)
    if st.session_state.search_engine:
        prompt = SEARCH_AND_RETRIEVAL_PROMPT.format(user_query=user_query)
    else:
        prompt = RETRIEVAL_ONLY_PROMPT.format(user_query=user_query)

    client = OpenAI(api_key=config_manager.get_key("OPENAI_API_KEY"))
    response =await asyncio.to_thread(client.chat.completions.create,
                              model="gpt-4o-mini",
                              messages=[{"role": "user", "content": prompt}])
    response_content = response.choices[0].message.content
    response_json =convert_to_json(response_content)

    # Extracting the search queries and retrieval subqueries
    internet_search_queries = response_json.get("internet_search_queries", [])
    retrieval_subqueries = response_json.get("retrieval_subqueries", [])

    # Ensure at least one retrieval subquery is present
    if not retrieval_subqueries:
        retrieval_subqueries = [user_query]

    return internet_search_queries, retrieval_subqueries

async def process_search_query(search_query):
    try:
        answer, sources = await get_search_answer(search_query)
        return {
            "query": search_query,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        print(f"Error in processing search query '{search_query}': {e}")
        return None

async def aggregate_search_results(search_queries):
    results = []

    tasks = [process_search_query(search_query) for search_query in search_queries]
    search_results = await asyncio.gather(*tasks)

    for result in search_results:
        if result is not None:
            results.append(result)

    return results