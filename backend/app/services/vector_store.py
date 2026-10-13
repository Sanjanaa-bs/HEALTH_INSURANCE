import os
import json
import tempfile
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.config import settings


class LocalVectorStore:
    """
    Persistent, lightweight Vector Store supporting Cosine Similarity search over embedded document chunks.
    Saves and loads index data atomically to/from a JSON vector index file.
    """

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or settings.VECTOR_STORE_PATH
        self.vectors: List[List[float]] = []
        self.metadata: List[Dict[str, Any]] = []

    def clear(self):
        """Reset index contents."""
        self.vectors = []
        self.metadata = []

    def add_chunk(
        self,
        chunk_id: int,
        document_id: int,
        document_title: str,
        document_type: str,
        version: Optional[str],
        page_number: Optional[int],
        printed_page_number: Optional[int],
        page_label: Optional[str],
        section_heading: Optional[str],
        text: str,
        content_hash: str,
        vector: List[float],
    ):
        """Add a single embedded chunk to vector index."""
        self.vectors.append(vector)
        self.metadata.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "document_title": document_title,
            "document_type": document_type,
            "version": version,
            "page_number": page_number,
            "printed_page_number": printed_page_number,
            "page_label": page_label,
            "section_heading": section_heading,
            "supporting_text": text,
            "content_hash": content_hash,
        })

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search vector store using dot product / cosine similarity.
        Returns top_k matching chunks with similarity scores.
        """
        if not self.vectors or not query_vector:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm < 1e-6:
            return []

        q_vec = q_vec / q_norm
        matrix = np.array(self.vectors, dtype=np.float32)

        # Compute cosine similarity
        similarities = np.dot(matrix, q_vec)

        results = []
        for idx, score in enumerate(similarities):
            meta = self.metadata[idx]

            # Apply document_type filter if specified
            if document_type and meta.get("document_type") != document_type:
                continue

            item = dict(meta)
            item["similarity_score"] = float(score)
            results.append(item)

        # Sort by highest cosine similarity
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def save(self, filepath: Optional[str] = None):
        """Persist vector index to JSON file."""
        target_path = filepath or self.filepath
        data = {
            "version": "1.0",
            "count": len(self.vectors),
            "vectors": self.vectors,
            "metadata": self.metadata,
        }
        parent = os.path.dirname(os.path.abspath(target_path))
        os.makedirs(parent, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=parent, delete=False
            ) as f:
                temp_path = f.name
                json.dump(data, f, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def load(self, filepath: Optional[str] = None) -> bool:
        """Load vector index from JSON file."""
        target_path = filepath or self.filepath
        if not os.path.exists(target_path):
            return False

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            vectors = data.get("vectors", [])
            metadata = data.get("metadata", [])
            if not isinstance(vectors, list) or not isinstance(metadata, list):
                return False
            if len(vectors) != len(metadata):
                return False
            if any(not isinstance(vector, list) for vector in vectors):
                return False
            self.vectors = vectors
            self.metadata = metadata
            return True
        except Exception:
            return False


# Global singleton instance shared by startup, retrieval, and indexing.
vector_store_instance = LocalVectorStore()
