"""Compatibility exports for the canonical vector store service."""
from backend.app.services.vector_store import LocalVectorStore, vector_store_instance

__all__ = ["LocalVectorStore", "vector_store_instance"]
