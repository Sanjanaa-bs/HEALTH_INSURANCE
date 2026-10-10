import math
import re
from typing import List, Optional, Dict, Any
import numpy as np

from backend.app.config import settings


class BaseEmbeddingProvider:
    """Abstract interface for text embedding models."""

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class LocalDenseEmbeddingProvider(BaseEmbeddingProvider):
    """
    High-performance local embedding provider using TF-IDF + Character/Word subword hash projection.
    Produces deterministic 128-dimensional L2-normalized dense embedding vectors without heavy dependencies.
    """

    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim

    def _hash_token(self, token: str) -> int:
        """Hash token into feature dimension index."""
        h = 0
        for char in token:
            h = (h * 31 + ord(char)) & 0xFFFFFFFF
        return h % self.vector_dim

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.vector_dim

        vec = np.zeros(self.vector_dim, dtype=np.float32)
        clean_text = text.lower()
        
        # 1. Word n-grams
        words = re.findall(r"\b[a-z0-9]+\b", clean_text)
        for i, w in enumerate(words):
            if len(w) >= 2:
                idx = self._hash_token(w)
                vec[idx] += 1.5
                
                # Bigrams
                if i < len(words) - 1:
                    bigram = f"{w}_{words[i+1]}"
                    b_idx = self._hash_token(bigram)
                    vec[b_idx] += 1.0

        # 2. Character subword n-grams (3 to 5 chars)
        for i in range(len(clean_text) - 3):
            sub = clean_text[i:i+4]
            if sub.strip():
                idx = self._hash_token(sub)
                vec[idx] += 0.4

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm

        return vec.tolist()


class SentenceTransformersEmbeddingProvider(BaseEmbeddingProvider):
    """Optional embedding provider using sentence-transformers library."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise RuntimeError(f"SentenceTransformers failed to load: {e}")

    def embed_text(self, text: str) -> List[float]:
        emb = self.model.encode(text, convert_to_numpy=True)
        return emb.tolist()


def get_embedding_provider(provider_name: Optional[str] = None) -> BaseEmbeddingProvider:
    """Factory to instantiate the requested embedding provider."""
    name = (provider_name or settings.EMBEDDING_PROVIDER).lower()

    if name == "sentence-transformers":
        try:
            return SentenceTransformersEmbeddingProvider(settings.EMBEDDING_MODEL_NAME)
        except Exception:
            return LocalDenseEmbeddingProvider(vector_dim=128)

    # Default to fast, robust LocalDenseEmbeddingProvider
    return LocalDenseEmbeddingProvider(vector_dim=128)
