import os

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

api_key =  os.getenv("OPENAI_API_KEY")

def get_retriever_from_documents(documents, top_k=4):
    """ 
    Generate retriever from documents

    Args:
        documents (list): List of documents.
        top_k (int): Top k of the document

    Returns:
        retriever (Retriever): The retriever.
    """
    print("Retriever is being invoked")
    text_splitter = CharacterTextSplitter(chunk_size=1000)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=api_key)

    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever(search_kwargs={"k": top_k})
    print(f"Retriever created with top k {top_k}")
    return retriever
