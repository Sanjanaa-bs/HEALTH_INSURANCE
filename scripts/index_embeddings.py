import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, init_db
from backend.app.models.document import Document, DocumentChunk
from backend.app.search import format_page_label
from backend.app.services.embeddings import get_embedding_provider
from backend.app.services.vector_store import LocalVectorStore, vector_store_instance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("index_embeddings")


def index_all_chunks(
    db: Session,
    provider_name: str = "local",
    output_path: Optional[str] = None,
    force_rebuild: bool = False,
) -> int:
    """
    Generate dense embeddings for all DocumentChunks in SQLite DB
    and persist them to LocalVectorStore.
    """
    logger.info(f"Starting document vector embedding indexing using provider '{provider_name}'...")
    embedder = get_embedding_provider(provider_name=provider_name)

    chunks = db.query(DocumentChunk).all()
    if not chunks:
        logger.warning("No DocumentChunks found in database. Run ingestion scripts first.")
        return 0

    logger.info(f"Loaded {len(chunks)} document chunks from database.")

    store = LocalVectorStore(filepath=output_path) if output_path else vector_store_instance
    store.clear()
    indexed_count = 0

    for chunk in chunks:
        doc = chunk.document
        doc_title = doc.title if doc else "Star Comprehensive Policy"
        doc_type = doc.document_type if doc else "policy"
        version = doc.version if doc else None

        total_pages = None
        if doc and doc.metadata_json:
            try:
                meta_dict = json.loads(doc.metadata_json) if isinstance(doc.metadata_json, str) else doc.metadata_json
                total_pages = meta_dict.get("extracted_pages") or meta_dict.get("total_pages")
            except Exception:
                pass

        printed_p, page_label = format_page_label(doc_type, chunk.page_number, total_pages=total_pages)

        text_to_embed = f"{doc_title} {chunk.section_heading or ''} {chunk.text}"
        vector = embedder.embed_text(text_to_embed)

        store.add_chunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_title=doc_title,
            document_type=doc_type,
            version=version,
            page_number=chunk.page_number,
            printed_page_number=printed_p,
            page_label=page_label or f"Page {chunk.page_number}",
            section_heading=chunk.section_heading,
            text=chunk.text,
            content_hash=chunk.content_hash or f"chunk_{chunk.id}",
            vector=vector,
        )
        indexed_count += 1

    store.save()
    logger.info(f"Successfully indexed and saved {indexed_count} vector embeddings to {store.filepath}")
    return indexed_count


def main():
    parser = argparse.ArgumentParser(description="Rebuild vector index for policy chunks.")
    parser.add_argument("--provider", choices=["local", "sentence-transformers"], default="local", help="Embedding provider")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path for vector index")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        index_all_chunks(db, provider_name=args.provider, output_path=args.output)
    finally:
        db.close()


if __name__ == "__main__":
    main()
