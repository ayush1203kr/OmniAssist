"""Lightweight RAG pipeline: policy documents -> ChromaDB + dense sentence
embeddings (sentence-transformers all-MiniLM-L6-v2).

Ingestion (scripts/ingest.py) stores the embedded chunks once; this module only
reads them back via top-k cosine-similarity search.
"""

from pathlib import Path

from langchain_core.embeddings import Embeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "chroma_db"  # vector DB is persisted here
COLLECTION_NAME = "policies"
TOP_K = 3  # number of policy chunks retrieved per query

# One embedding model / one vector store per process, created on first use.
_cache: dict = {}


class MiniLMEmbeddings(Embeddings):
    """Turn text into dense vectors with sentence-transformers' all-MiniLM-L6-v2.

    Implements LangChain's small Embeddings interface (embed_documents /
    embed_query) so it plugs straight into ChromaDB. Vectors are L2-normalised,
    which makes the similarity search a true cosine-similarity lookup.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Imported here so that importing this module stays cheap.
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


def get_embedding_function() -> MiniLMEmbeddings:
    """Load the embedding model once and reuse it."""
    if "embeddings" not in _cache:
        _cache["embeddings"] = MiniLMEmbeddings()
    return _cache["embeddings"]


def get_vectorstore():
    """Open the persisted ChromaDB collection (created by scripts/ingest.py)."""
    if "store" not in _cache:
        from langchain_chroma import Chroma  # imported here to keep start-up fast

        _cache["store"] = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
            persist_directory=str(CHROMA_PATH),
            collection_metadata={"hnsw:space": "cosine"},  # cosine similarity
        )
    return _cache["store"]


def retrieve_policy(query: str, k: int = TOP_K) -> str:
    """Retrieve the top-k policy chunks most similar to the query."""
    docs = get_vectorstore().similarity_search(query, k=k)
    if not docs:
        # Nothing indexed yet (ingest script not run) — the agent says so honestly.
        return ""
    return "\n\n".join(doc.page_content for doc in docs)
