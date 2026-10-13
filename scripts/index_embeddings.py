import sys
import os
import logging
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, init_db
from backend.app.models.document import Document, DocumentChunk
from backend.app.services.embeddings import get_embedding_provider
from backend.app.services.vector_store import vector_store_instance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("index_embeddings")


def index_all_chunks(db: Session, force_rebuild: bool = False):
    """
    Generate dense embeddings for all DocumentChunks in SQLite DB
    and persist them to LocalVectorStore (vector_index.json).
    """
    logger.info("Starting document vector embedding indexing...")
    embedder = get_embedding_provider()

    chunks = db.query(DocumentChunk).all()
    if not chunks:
        logger.warning("No DocumentChunks found in database. Run ingestion scripts first.")
        vector_store_instance.clear()
        vector_store_instance.save()
        return 0

    logger.info(f"Loaded {len(chunks)} document chunks from database.")

    vector_store_instance.clear()
    indexed_count = 0

    for chunk in chunks:
        doc = chunk.document
        doc_title = doc.title if doc else "Star Comprehensive Policy"
        doc_type = doc.document_type if doc else "policy"
        version = doc.version if doc else None

        page_label = f"Physical Page {chunk.page_number}"
        if doc and doc.document_type == "policy" and chunk.page_number and chunk.page_number > 1:
            printed_p = chunk.page_number - 1
            page_label = f"Physical Page {chunk.page_number} (Printed Page {printed_p}/47)"
        elif doc and doc.document_type == "cis" and chunk.page_number and chunk.page_number > 1:
            printed_p = chunk.page_number - 1
            page_label = f"Physical Page {chunk.page_number} (Printed Page {printed_p}/19)"

        text_to_embed = f"{doc_title} {chunk.section_heading or ''} {chunk.text}"
        vector = embedder.embed_text(text_to_embed)

        vector_store_instance.add_chunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_title=doc_title,
            document_type=doc_type,
            version=version,
            page_number=chunk.page_number,
            printed_page_number=chunk.page_number - 1 if chunk.page_number and chunk.page_number > 1 else chunk.page_number,
            page_label=page_label,
            section_heading=chunk.section_heading,
            text=chunk.text,
            content_hash=chunk.content_hash or f"chunk_{chunk.id}",
            vector=vector,
        )
        indexed_count += 1

    vector_store_instance.save()
    logger.info(f"Successfully indexed and saved {indexed_count} vector embeddings to {vector_store_instance.filepath}")
    return indexed_count


def main():
    init_db()
    db = SessionLocal()
    try:
        index_all_chunks(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
