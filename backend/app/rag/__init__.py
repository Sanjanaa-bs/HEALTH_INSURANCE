"""
Backward-Compatibility Facade Package (RAG Shim)

This package preserves backward compatibility for legacy imports referencing
`backend.app.rag.*` (such as test harnesses or external scripts) by re-exporting
the canonical implementations from `backend.app.services.*`.
"""
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
