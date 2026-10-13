from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.search import search_document_chunks
from backend.app.services.embeddings import get_embedding_provider
from backend.app.services.vector_store import vector_store_instance


def hybrid_search(
    db: Session,
    query_text: str,
    document_type: Optional[str] = None,
    top_k: int = 5,
    alpha: float = 0.5,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Perform hybrid retrieval:
    1. BM25 keyword search via SQLite FTS5 index.
    2. Dense Vector semantic search via LocalVectorStore.
    3. RRF / Score Fusion to rank combined results.
    4. Deduplication by chunk_id.

    Returns:
        (ranked_passages, retrieval_mode)
    """
    clean_query = query_text.strip()
    if not clean_query:
        return [], "none"

    # 1. BM25 Keyword Search
    bm25_results = search_document_chunks(
        db=db,
        query_text=clean_query,
        document_type=document_type,
        limit=top_k * 2,
    )

    # 2. Vector Semantic Search
    if not vector_store_instance.vectors:
        vector_store_instance.load()

    embedder = get_embedding_provider()
    query_vector = embedder.embed_text(clean_query)
    vector_results = vector_store_instance.search(
        query_vector=query_vector,
        top_k=top_k * 2,
        document_type=document_type,
    )

    # Determine retrieval mode
    if vector_results and bm25_results:
        retrieval_mode = "hybrid"
    elif vector_results:
        retrieval_mode = "vector"
    else:
        retrieval_mode = "keyword"

    # 3. Combine & Rank Results via Reciprocal Rank Fusion (RRF)
    combined: Dict[int, Dict[str, Any]] = {}
    rrf_k = 60.0

    # Add weighted BM25 RRF scores. Alpha=1 is keyword-only; alpha=0 is vector-only.
    for rank, item in enumerate(bm25_results):
        cid = item["chunk_id"]
        rrf_score = alpha / (rrf_k + rank + 1)
        
        passage_data = dict(item)
        passage_data["supporting_text"] = item.get("excerpt", "").replace("<b>", "").replace("</b>", "").strip()
        passage_data["rrf_score"] = rrf_score
        passage_data["bm25_rank"] = rank + 1
        combined[cid] = passage_data

    # Add Vector RRF scores
    for rank, item in enumerate(vector_results):
        cid = item["chunk_id"]
        v_rrf_score = (1.0 - alpha) / (rrf_k + rank + 1)

        if cid in combined:
            combined[cid]["rrf_score"] += v_rrf_score
            combined[cid]["vector_rank"] = rank + 1
            combined[cid]["similarity_score"] = item.get("similarity_score", 0.0)
        else:
            passage_data = dict(item)
            passage_data["rrf_score"] = v_rrf_score
            passage_data["vector_rank"] = rank + 1
            combined[cid] = passage_data

    # 4. Sort by RRF score descending and deduplicate
    final_ranked = list(combined.values())
    final_ranked.sort(key=lambda x: x["rrf_score"], reverse=True)

    return final_ranked[:top_k], retrieval_mode
