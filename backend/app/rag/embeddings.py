"""Compatibility exports for the canonical embedding service."""
from backend.app.services.embeddings import (
    BaseEmbeddingProvider,
    LocalDenseEmbeddingProvider,
    SentenceTransformersEmbeddingProvider,
    get_embedding_provider,
)

__all__ = [
    "BaseEmbeddingProvider",
    "LocalDenseEmbeddingProvider",
    "SentenceTransformersEmbeddingProvider",
    "get_embedding_provider",
]
