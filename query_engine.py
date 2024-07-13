import os
import time

import chromadb
from llama_index.core import StorageContext,VectorStoreIndex,ServiceContext,Document

from llama_index.core.node_parser import TokenTextSplitter
from custom_query_engine import RAGStringQueryEngine
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.get_or_create_collection("chatbot-3")

api_key =  os.getenv("OPENAI_API_KEY")


def get_documents_from_text(text,filename,start_index):
    text_splitter = TokenTextSplitter(chunk_size=400)
    chunks=text_splitter.split_text(text)
    documents = generate_documents_from_chunks(chunks,filename,start_index)
    return documents


def get_query_engine_from_text(documents, top_k=12):
    """ 
    Generate retriever from text

    Args:
        text (list):  text.
        top_k (int): Top k of the document

    Returns:
        retriever (Retriever): The retriever.
    """
    print("Retriever is being invoked")
    current_time = time.time()
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embeddings = OpenAIEmbedding(api_key=api_key,show_progress_bar=True,embed_batch_size=100)
    service_context = ServiceContext.from_defaults(embed_model=embeddings)
    
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context,service_context=service_context
    )   
    retriever = index.as_retriever(similarity_top_k=top_k)

    query_engine = RAGStringQueryEngine(
        retriever=retriever
    )
    print(f"Retriever created with top k {top_k}")
    print("Completed the function in :",time.time()-current_time)

    return query_engine


def generate_documents_from_chunks(chunks,filename,start_index=1):
    documents = []
    for idx,txt in enumerate(chunks,start=start_index):
        document = Document(
            doc_id = idx,
            text = txt,
            metadata={"filename": f"{filename}"},
        )
        documents.append(document)
    
    return documents


def get_all_ids():
    all_ids = chroma_collection.get()['ids']
    print("All ids :",len(all_ids))
    return all_ids

def reset_collection():
    all_ids = chroma_collection.get()['ids']
    total_ids = len(all_ids)
    batch_size = 100
    
    for i in range(0, total_ids, batch_size):
        batch = all_ids[i:i+batch_size]
        chroma_collection.delete(ids=batch)
        print(f"Deleted batch {i//batch_size + 1}: {len(batch)} documents")
    
    print(f"Cleared {total_ids} documents from the collection.")

