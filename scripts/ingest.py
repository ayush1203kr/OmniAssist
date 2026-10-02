"""One-time ingestion: policy .txt files -> chunks -> dense embeddings -> ChromaDB.

Run this once from the project root before starting the API:
    python scripts/ingest.py
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag import CHROMA_PATH, COLLECTION_NAME, get_embedding_function

DATA_DIR = PROJECT_ROOT / "data"

def load_documents(data_dir: Path) -> list[Document]:
    documents = []
    for txt_file in sorted(data_dir.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        documents.append(Document(page_content=text, metadata={"source": txt_file.name}))
    return documents

def main() -> None:
    print("Loading documents...")
    documents = load_documents(DATA_DIR)
    print(f"Loaded {len(documents)} policy documents.")
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)
    print("Creating embeddings and storing documents in ChromaDB...")
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_function(),
        persist_directory=str(CHROMA_PATH),
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print("Ingestion completed successfully.")

if __name__ == "__main__":
    main()
