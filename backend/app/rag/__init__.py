"""RAG module package initialization."""
from backend.app.rag.embeddings import get_embedding_provider, BaseEmbeddingProvider, LocalDenseEmbeddingProvider
from backend.app.rag.vector_store import vector_store_instance, LocalVectorStore
from backend.app.rag.retrieval import hybrid_search
from backend.app.rag.llm_provider import get_llm_provider, BaseLLMProvider

__all__ = [
    "get_embedding_provider",
    "BaseEmbeddingProvider",
    "LocalDenseEmbeddingProvider",
    "vector_store_instance",
    "LocalVectorStore",
    "hybrid_search",
    "get_llm_provider",
    "BaseLLMProvider",
]
