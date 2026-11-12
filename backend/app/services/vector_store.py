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

    def rebuild_from_database(self, db, embedder=None, save: bool = True) -> int:
        """Embed every DocumentChunk in the database and replace the index contents."""
        from backend.app.models.document import DocumentChunk
        from backend.app.services.embeddings import get_embedding_provider

        embedder = embedder or get_embedding_provider()
        self.clear()
        for chunk in db.query(DocumentChunk).order_by(DocumentChunk.id).all():
            meta = _chunk_metadata(chunk)
            text_to_embed = f"{meta['document_title']} {chunk.section_heading or ''} {chunk.text}"
            self.vectors.append(embedder.embed_text(text_to_embed))
            self.metadata.append(meta)
        if save:
            self.save()
        return len(self.vectors)

    def reconcile_with_database(self, db, embedder=None) -> str:
        """
        Align the loaded index with the chunks currently stored in the database.

        The index file is portable between machines but chunk/document IDs are not:
        re-running ingestion assigns new auto-increment IDs. Entries are therefore
        matched by content hash and their IDs and citation metadata refreshed from the
        database. If the chunk contents or embedding dimensions differ, the index is
        rebuilt and saved.

        Returns "in_sync", "remapped", or "rebuilt".
        """
        from backend.app.models.document import DocumentChunk
        from backend.app.services.embeddings import get_embedding_provider

        embedder = embedder or get_embedding_provider()
        chunks = db.query(DocumentChunk).all()
        by_hash = {c.content_hash: c for c in chunks if c.content_hash}

        index_hashes = [m.get("content_hash") for m in self.metadata]
        expected_dim = len(embedder.embed_text("dimension probe"))
        content_matches = (
            len(self.vectors) == len(chunks)
            and len(by_hash) == len(chunks)
            and set(index_hashes) == set(by_hash)
        )
        dims_match = all(len(v) == expected_dim for v in self.vectors)

        if not content_matches or not dims_match:
            self.rebuild_from_database(db, embedder=embedder)
            return "rebuilt"

        changed = False
        for idx, content_hash in enumerate(index_hashes):
            fresh = _chunk_metadata(by_hash[content_hash])
            if self.metadata[idx] != fresh:
                self.metadata[idx] = fresh
                changed = True
        return "remapped" if changed else "in_sync"


def _chunk_metadata(chunk) -> Dict[str, Any]:
    """Build citation metadata for a chunk, matching the FTS5 search result format."""
    from backend.app.search import format_page_label

    doc = chunk.document
    doc_type = doc.document_type if doc else "policy"
    printed_page, page_label = format_page_label(doc_type, chunk.page_number)
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "document_title": doc.title if doc else "Star Comprehensive Policy",
        "document_type": doc_type,
        "version": doc.version if doc else None,
        "page_number": chunk.page_number,
        "printed_page_number": printed_page,
        "page_label": page_label,
        "section_heading": chunk.section_heading,
        "supporting_text": chunk.text,
        "content_hash": chunk.content_hash or f"chunk_{chunk.id}",
    }


# Global singleton instance shared by startup, retrieval, and indexing.
vector_store_instance = LocalVectorStore()
