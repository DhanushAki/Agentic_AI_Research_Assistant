import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# Configuration
DATA_PATH = "data/"
CHROMA_PATH = "chroma_db"

def main():
    # 1. Load documents (PDF and TXT)
    documents = load_documents()
    
    # 2. Split into chunks
    chunks = split_documents(documents)
    
    # 3. Add to Chroma with ID-based incremental loading
    add_to_chroma(chunks)

def load_documents():
    print(f"--- Loading documents from {DATA_PATH} ---")
    
    # Load Text Files
    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    # Load PDF Files
    pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    
    docs = txt_loader.load() + pdf_loader.load()
    print(f"Loaded {len(docs)} documents.")
    return docs

def split_documents(documents: list[Document]):
    print("--- Splitting documents ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Day 7: Add prefix for Nomic Embeddings
    for chunk in chunks:
        chunk.page_content = f"search_document: {chunk.page_content}"
        
    return chunks

def calculate_chunk_ids(chunks):
    """
    Creates unique IDs for chunks: "data/source.pdf:page:chunk_index"
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", 0) # PDF pages start at 0
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def add_to_chroma(chunks: list[Document]):
    print("--- Adding to Vector Store ---")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    embeddings = OllamaEmbeddings(model="qwen2.5-coder:7b", base_url=ollama_base_url)
    
    # Initialize Chroma and persist immediately
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embeddings
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[]) 
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        print("✅ Database persisted successfully!")
    else:
        print("✅ No new documents to add")

def clear_database():
    if os.path.exists(CHROMA_PATH):
        print("--- Clearing Database ---")
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    main()
