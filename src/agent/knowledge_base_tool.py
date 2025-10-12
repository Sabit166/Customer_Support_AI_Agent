"""
Knowledge Base Tool for Customer Support AI Agent
Handles service inquiries about company information, packages, policies, and support
"""

from concurrent.futures import thread
import json
from datetime import datetime
from .knowledge_base import knowledge_base
from typing import Optional
from agents import function_tool


# Import Libraries for RAG
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document

import threading
import subprocess
import time

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

embedding_model=OllamaEmbeddings(model="all-minilm")


@function_tool
def search_knowledge_base(query: str, category: Optional[str] = None) -> str:
    """
    Search the knowledge base for information about company services, policies, and support.
    
    Args:
        query: The user's question or search term
        category: Optional category to filter results (packages, policies, support, hours)
    
    Returns:
        JSON string with relevant information from the knowledge base
    """
    
    # Convert dictionary knowledge base to LangChain Documents
    documents = []
    
    def dict_to_documents(data, category_prefix=""):
        """Recursively convert dictionary to Document objects"""
        docs = []
        for key, value in data.items():
            if isinstance(value, dict):
                if "name" in value or "description" in value:
                    # This is a leaf node with actual content
                    content = ""
                    metadata = {"category": category_prefix or key}
                    
                    for k, v in value.items():
                        if isinstance(v, list):
                            content += f"{k}: {', '.join(v)}\n"
                        elif isinstance(v, str):
                            content += f"{k}: {v}\n"
                            if k == "name":
                                metadata["name"] = v
                    
                    docs.append(Document(page_content=content.strip(), metadata=metadata))
                else:
                    # Recurse deeper
                    docs.extend(dict_to_documents(value, f"{category_prefix}_{key}" if category_prefix else key))
            elif isinstance(value, (str, list)):
                # Direct string or list content
                content = f"{key}: {value if isinstance(value, str) else ', '.join(value)}"
                docs.append(Document(page_content=content, metadata={"category": category_prefix or "general"}))
        return docs
    
    documents = dict_to_documents(knowledge_base)
    
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    
    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Perform similarity search
    relevant_docs = vector_store.similarity_search(query, k=3)
    
    # Format results
    results = []
    for doc in relevant_docs:
        results.append({
            "content": doc.page_content,
            "category": doc.metadata.get("category", "unknown"),
            "relevance": "high"  # Could add scoring here
        })
    
    return json.dumps({
        "query": query,
        "category": category,
        "results": results,
        "total_found": len(results),
        "search_method": "vector_similarity"
    }, indent=2) 