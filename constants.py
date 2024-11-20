import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_MODEL="gpt-4o"
CLAUDE_MODEL="claude-3-5-sonnet-20240620"

short_book_generator_prompt = """
You are an AI writing assistant tasked with creating a short book on a specific subtopic from a larger book. The input you will receive includes:

1. A brief summary of the subtopic (1-2 sentences)
2. The context around the subtopic from the original book (a few paragraphs)

Your task is to use the provided summary and context to generate a well-formatted and comprehensive short book on the subtopic, following the given structure and guidelines.

Subtopic Summary: {subtopic_summary}

Context from the Book: {context}

Your short book should include the following sections:

1. Introduction (1-2 paragraphs): Provide an overview of the subtopic and its relevance or importance, deriving information from the provided context.

2. Background (2-4 paragraphs): Give necessary background information, historical context, or foundational concepts related to the subtopic, based on the provided context.

3. Key Points (3-5 sections, each with 2-4 paragraphs): Elaborate on the main ideas, theories, or components of the subtopic, using the provided context as a starting point, and expanding on it with your own knowledge and understanding.

4. Examples (1-2 paragraphs per key point): Provide real-world examples, case studies, or practical applications to illustrate each key point, drawing from the context and your own knowledge.

5. Conclusion (1-2 paragraphs): Summarize the main takeaways and potential future developments or research directions related to the subtopic, based on the information in the context and your own understanding.

Additionally, your short book should:

- Use appropriate section headings and subheadings for better organization.
- Include in-text citations or references to the original book when using direct quotes or paraphrasing from the provided context.
- Maintain a consistent and easy-to-follow writing style suitable for a general audience.
- Be around 2,000-3,000 words in length.
- Keep the content focused on the provided subtopic summary and context, while expanding on it with your own knowledge and understanding.

Please let me know if you need any clarification or have additional requirements for the short book.
"""

SHORT_BOOk_GENERATOR = """
You are an AI tasked with creating a short book on a subtopic from a larger book. 
Generate a short book with the following sections:

1. Introduction (1-2 paragraphs)
2. Background (2-4 paragraphs)  
3. Key Points (3-5 sections, 2-4 paragraphs each)
4. Examples (1-2 paragraphs per key point)
5. Conclusion (1-2 paragraphs)

Guidelines:
- Use section headings/subheadings
- Cite original book when quoting/paraphrasing
- 1000-2000 words

Output: A formatted short book on the subtopic.

Input:
1. Subtopic Summary: {subtopic_summary}
2. Context from Book: {context}

Output:

"""

BOOK_GENERATOR = """
You are a world-leading expert in the relevant field or domain. 
Provide a comprehensive, technical, and contextually relevant response to the following query using the provided context and search results.
Do not provide conclusion , instead, focus on elaborating on the key points as much as possible in depth. 
Your response should be as detail as possible. 
Begin your response with a brief title in H2 Markdown.

Context: {context}
Query: {query}

Search Queries and Answers:
{search_results}

Response:
"""

BOOK_GENERATOR_V2="""
As a leading expert in the field, create a comprehensive and detailed document addressing the following query. Use the provided context and search results to inform your response.

Guidelines:
1. Structure the document based on the query's context and complexity.
2. Provide in-depth explanations for each point, concept, or idea.
3. Cover all relevant aspects, even those not explicitly mentioned in the query.
4. Ignore token limits; focus on thorough exploration of the topic.
5. Maintain technical accuracy and clarity.
6. Use Markdown formatting to enhance readability.
7. Do not provide a conclusion or summary section under any circumstances.

Most Important Guidenline:
1.If you reach a point where you would normally stop, instead transition to the next relevant subtopic or aspect of the query.
2.Begin with a descriptive H1 Markdown title.

Context: {context}
Query: {query}

Search Results:
{search_results}

Response:

"""

TOP_K = 12


SEARCH_AND_RETRIEVAL_PROMPT = """
You are an AI assistant specialized in parsing complex queries to identify distinct search tasks and subqueries for retrieval. 
For each user query, separate the overall request into:

1. Internet search queries (limited to 4 and concise).
2. Subqueries for retrieving content from uploaded items.

Instructions:
1. Read the user's query carefully.
2. Identify distinct search tasks or components within the query.
3. List each search task separately for targeted searches, limiting to a maximum of 3 queries.
4. Generate subqueries for retrieving content from uploaded items, ensuring all queries are concise. 
   Limit to a maximum of 3 and minimum of 1 query. Only generate search queries if needed.

Example Query:
Look online and research NinePoint Medical. Create a detailed analysis of what the company makes (by product name if possible), 
who they sell to (specifically), and who their target market is. Include any information about their manufacturing practice, 
key people, key metrics (size, location, personnel count, reputation), and contact info. Do not make up information.

Output:
{{
  "query": "Look online and research NinePoint Medical. Create a detailed analysis of what the company makes (by product name if possible), 
  who they sell to (specifically), and who their target market is. Include any information about their manufacturing practice, 
  key people, key metrics (size, location, personnel count, reputation), and contact info. Do not make up information.",
  "internet_search_queries": [
    "NinePoint Medical product line",
    "NinePoint Medical target market",
    "NinePoint Medical key people and contact information",
  ],
  "retrieval_subqueries": [
    "Manufacturing practices of NinePoint Medical",
    "Key metrics of NinePoint Medical",
    "Size and location of NinePoint Medical",
    "Personnel count of NinePoint Medical"
  ]
}}

User Query: {user_query}

Response (in JSON format):
"""

RETRIEVAL_ONLY_PROMPT = """
You are an AI assistant specialized in parsing complex queries to identify subqueries for retrieving content from uploaded items. 
For each user query, identify distinct subqueries for retrieval.

Instructions:
1. Read the user's query carefully.
2. Generate subqueries for retrieving content from uploaded items, ensuring all queries are concise. 
   Limit to a maximum of 3 and minimum of 1 query.

Example Query:
Analyze uploaded documents to extract financial data, summarize project timelines, and identify stakeholders.

Output:
{{
  "query": "Analyze uploaded documents to extract financial data, summarize project timelines, and identify stakeholders.",
  "retrieval_subqueries": [
    "Extract financial data from uploaded documents",
    "Summarize project timelines from uploaded documents",
    "Identify stakeholders from uploaded documents"
  ]
}}

User Query: {user_query}

Response (in JSON format):
"""

ENCRYPTED_KEYS_FILE_PATH = 'api_keys.json'
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Performance Requirements: The requirements cover various aspects like color rendering, illumination, spatial frequency response, resolution, mechanical interface, safety measures, and noise levels.
# |
# Functional Requirements: The system should have functions like brightness, gamma, sharpness, color adjustment, white balance, screen freeze, image magnification, endoscopic mode switching, language selection, shortcut buttons, video/photo capture, data storage, reset, and soft lens interface.


