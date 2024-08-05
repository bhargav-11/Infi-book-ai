import os
import json
from openai import OpenAI
from tavily import TavilyClient
import asyncio

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key =  os.getenv("TAVILY_API_KEY")

async def get_answer(query,context):
    prompt = (
      "You are an AI assistant specialized in answers to query using the provided context."
      "Please make sure to provide answer from the provided context"
      f"Query: {query}\n\n"
      f"Context: {context}\n\n"
      "Answer:"
    )
    client = OpenAI(api_key=openai_api_key)
    response = await asyncio.to_thread(client.chat.completions.create,
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}])
    response_content = response.choices[0].message.content
    return response_content


async def get_query_context(query):
    tavily_client = TavilyClient(api_key=tavily_api_key)

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
    prompt = (
    "You are an AI assistant specialized in parsing complex queries to identify distinct search tasks and subqueries for retrieval. "
    "For each user query, separate the overall request into:\n"
    "1. Internet search queries (limited to 4 and concise).\n"
    "2. Subqueries for retrieving content from uploaded items.\n\n"
    "Instructions:\n"
    "1. Read the user's query carefully.\n"
    "2. Identify distinct search tasks or components within the query.\n"
    "3. List each search task separately for targeted searches, limiting to a maximum of 3 queries.\n"
    "4. Generate subqueries for retrieving content from uploaded items, "
    "ensuring all queries are concise.Limit to a maximum of 3 and minimum of 1 query.Only generate search queries if needed.\n\n"
    "Example Query:\n"
    "Look online and research NinePoint Medical. Create a detailed analysis of what the company makes (by product name if possible), "
    "who they sell to (specifically), and who their target market is. Include any information about their manufacturing practice, "
    "key people, key metrics (size, location, personnel count, reputation), and contact info. Do not make up information.\n\n"
    "Output:\n"
    "{\n"
    '  "query": "Look online and research NinePoint Medical. Create a detailed analysis of what the company makes (by product name if possible), '
    'who they sell to (specifically), and who their target market is. Include any information about their manufacturing practice, '
    'key people, key metrics (size, location, personnel count, reputation), and contact info. Do not make up information.",\n'
    '  "internet_search_queries": [\n'
    '    "NinePoint Medical product line",\n'
    '    "NinePoint Medical target market",\n'
    '    "NinePoint Medical key people and contact information",\n'
    "  ],\n"
    '  "retrieval_subqueries": [\n'
    '    "Manufacturing practices of NinePoint Medical",\n'
    '    "Key metrics of NinePoint Medical",\n'
    '    "Size and location of NinePoint Medical",\n'
    '    "Personnel count of NinePoint Medical"\n'
    "  ]\n"
    "}\n"
    f"User Query: {user_query}\n\n"
    "Response (in JSON format):"
    )
    client = OpenAI(api_key=openai_api_key)
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