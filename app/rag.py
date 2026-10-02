"""Lightweight policy RAG using ChromaDB and all-MiniLM-L6-v2."""
from pathlib import Path
from langchain_core.embeddings import Embeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "policies"
TOP_K = 3
_cache = {}

class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()

def get_embedding_function() -> MiniLMEmbeddings:
    if "embeddings" not in _cache:
        _cache["embeddings"] = MiniLMEmbeddings()
    return _cache["embeddings"]

def get_vectorstore():
    if "store" not in _cache:
        from langchain_chroma import Chroma
        _cache["store"] = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
            persist_directory=str(CHROMA_PATH),
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _cache["store"]

def retrieve_policy(query: str, k: int = TOP_K) -> str:
    docs = get_vectorstore().similarity_search(query, k=k)
    return "\n\n".join(doc.page_content for doc in docs) if docs else ""
