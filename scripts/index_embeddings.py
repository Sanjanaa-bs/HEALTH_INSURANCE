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

    indexed_count = vector_store_instance.rebuild_from_database(db, embedder=embedder, save=False)

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
