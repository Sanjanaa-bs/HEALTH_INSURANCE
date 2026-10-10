import email
import hashlib
import json
import logging
import re
import sys
from email import policy
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, init_db
from backend.app.models.document import Document, DocumentChunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_claim_guidance")


def extract_mhtml_text_and_chunks(
    html_content: str, doc_title: str
) -> List[Dict[str, Any]]:
    """Extract readable text passages from MHTML document preserving section headings."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content elements
    for el in soup(["script", "style", "nav", "header", "footer", "noscript", "svg"]):
        el.extract()

    chunks = []
    chunk_idx = 0

    # Extract by logical section containers or heading-driven blocks
    headings = soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "dt", "dd"])
    current_heading = doc_title
    current_passage = []

    for el in headings:
        tag_name = el.name.lower()
        text = el.get_text().strip()
        if not text or len(text) < 5:
            continue

        if tag_name in ["h1", "h2", "h3", "h4"]:
            current_heading = text
            continue

        current_passage.append(text)
        combined = " ".join(current_passage)

        if len(combined) >= 800:
            content_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            chunks.append({
                "text": combined,
                "page_number": 1,
                "section_heading": current_heading,
                "chunk_index": chunk_idx,
                "content_hash": content_hash,
                "token_count": len(combined.split()),
            })
            chunk_idx += 1
            current_passage = []

    if current_passage:
        combined = " ".join(current_passage)
        if len(combined.strip()) > 50:
            content_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            chunks.append({
                "text": combined,
                "page_number": 1,
                "section_heading": current_heading,
                "chunk_index": chunk_idx,
                "content_hash": content_hash,
                "token_count": len(combined.split()),
            })

    return chunks


def ingest_claim_guidance_mhtml(
    guidance_dir: str = "data/claim_guidance",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Parse and ingest all saved claim guidance and FAQ MHTML documents.
    Preserves readable text, section headings, and original source URLs.
    """
    dir_path = Path(guidance_dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"Claim guidance directory not found at {guidance_dir}")

    should_close_db = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close_db = True

    metrics = {
        "files_scanned": 0,
        "documents_created": 0,
        "documents_updated": 0,
        "total_chunks_indexed": 0,
        "unparseable_files": [],
    }

    mhtml_files = sorted(dir_path.glob("*.mhtml"))

    for file_path in mhtml_files:
        metrics["files_scanned"] += 1
        logger.info(f"Processing claim guidance MHTML: {file_path.name}")
        norm_source_path = str(file_path).replace("\\", "/")

        try:
            with open(file_path, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
        except Exception as e:
            logger.error(f"Failed to open MIME message from {file_path.name}: {e}")
            metrics["unparseable_files"].append({"file": file_path.name, "error": str(e)})
            continue

        raw_subject = msg.get("Subject") or file_path.stem.replace("_", " ").title()
        source_url = msg.get("Snapshot-Content-Location") or ""
        doc_type = "faq" if "irdai" in file_path.name.lower() or "faq" in file_path.name.lower() else "claim_guidance"

        body = msg.get_body(preferencelist=("html", "plain"))
        if not body:
            logger.warning(f"No HTML/text body part in {file_path.name}")
            metrics["unparseable_files"].append({"file": file_path.name, "error": "No HTML/plain body found"})
            continue

        html_content = body.get_content()
        chunks = extract_mhtml_text_and_chunks(html_content, raw_subject)

        # Check existing document record for idempotency
        existing_doc = db.query(Document).filter(Document.source_path == norm_source_path).first()
        if existing_doc:
            doc = existing_doc
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            metrics["documents_updated"] += 1
        else:
            doc = Document(
                title=raw_subject,
                document_type=doc_type,
                source_path=norm_source_path,
                file_format="mhtml",
                file_size_bytes=file_path.stat().st_size,
                is_processed=len(chunks) > 0,
            )
            db.add(doc)
            db.flush()
            metrics["documents_created"] += 1

        doc.metadata_json = json.dumps({
            "source_url": source_url,
            "extraction_status": "success" if chunks else "empty_body",
            "chunks_count": len(chunks),
        })

        chunk_objects = [
            DocumentChunk(
                document_id=doc.id,
                text=c["text"],
                page_number=c["page_number"],
                section_heading=c["section_heading"],
                chunk_index=c["chunk_index"],
                content_hash=c["content_hash"],
                token_count=c["token_count"],
            )
            for c in chunks
        ]

        if chunk_objects:
            db.bulk_save_objects(chunk_objects)
            metrics["total_chunks_indexed"] += len(chunk_objects)

        db.commit()
        logger.info(f"Indexed {len(chunk_objects)} chunks from {file_path.name}.")

    if should_close_db:
        db.close()

    logger.info(
        f"Completed Claim Guidance Ingestion: {metrics['files_scanned']} files scanned, "
        f"{metrics['total_chunks_indexed']} chunks indexed, "
        f"{len(metrics['unparseable_files'])} unparseable file(s)."
    )
    return metrics


if __name__ == "__main__":
    ingest_claim_guidance_mhtml()
