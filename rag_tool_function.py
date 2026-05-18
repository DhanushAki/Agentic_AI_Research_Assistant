import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
CHROMA_PATH = "chroma_db"

@tool
def search_documents(query: str, k: int = 5):
    """
    Search local documents for information. Use this when the user asks specific questions about uploaded files or research papers.
    Returns: (context_string, forensic_data)
    """
    print(f"--- RAG TOOL: Retrieving for Lab: '{query}' (k={k}) ---")
    
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    embeddings = OllamaEmbeddings(model="qwen2.5-coder:7b", base_url=ollama_base_url)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Use similarity_search_with_score to get the L2 distances (Scores)
    results = db.similarity_search_with_score(query, k=k)
    
    # 1. Create the context string for the LLM
    context_text = "\n\n".join([doc.page_content for doc, score in results])
    
    # 2. Create a list of dictionaries for the Search Lab UI
    raw_data = []
    for doc, score in results:
        raw_data.append({
            "content": doc.page_content[:200] + "...",
            "score": round(float(score), 4),
            "metadata": doc.metadata
        })
        
    return context_text, raw_data

def retrieve_rag_context(query: str, k: int = 5):
    """Legacy helper for direct calls (used by main.py / app.py for forensics)"""
    return search_documents.invoke({"query": query, "k": k})

if __name__ == "__main__":
    context, raw = retrieve_rag_context("test")
    print(f"Retrieved {len(raw)} chunks.")
