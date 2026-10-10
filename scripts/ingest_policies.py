import hashlib
import json
import logging
import re
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Dict, Any, List, Optional
import pypdf
import pymupdf
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, init_db
from backend.app.models.document import Document, DocumentChunk
from backend.app.search import sync_fts5_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_policies")


def extract_headings_and_chunks(
    text: str, page_num: int, start_chunk_idx: int
) -> List[Dict[str, Any]]:
    """Split page text into chunks while capturing section heading context cleanly."""
    raw_lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not raw_lines:
        return []

    # Clean out repetitive page header / footer artifacts
    lines = []
    for line in raw_lines:
        if re.match(r"^\d+\s*/\s*47$", line):
            continue
        if "STAR HEALTH AND ALLIED INSURANCE COMPANY LIMITED" in line and "POLICY WORDINGS" in line:
            continue
        if "SHAHLIP26044V092526" in line and "V.24 / 2025" in line:
            continue
        lines.append(line)

    if not lines:
        return []

    current_heading = None
    chunks = []
    current_chunk_lines = []
    chunk_idx = start_chunk_idx

    for line in lines:
        # Detect section headings
        if (
            len(line) < 80
            and not line.startswith("Note:")
            and (
                line.isupper()
                or re.match(r"^(section|clause|part|table|item|coverage|benefit|exclusion|condition|preamble|definitions)\b", line, re.I)
                or line.endswith(":")
            )
        ):
            current_heading = line.rstrip(":")

        current_chunk_lines.append(line)
        joined_text = " ".join(current_chunk_lines)

        # Chunk threshold around 800 - 1000 characters
        if len(joined_text) >= 800:
            content_hash = hashlib.sha256(joined_text.encode("utf-8")).hexdigest()
            chunks.append({
                "text": joined_text,
                "page_number": page_num,
                "section_heading": current_heading or f"Page {page_num}",
                "chunk_index": chunk_idx,
                "content_hash": content_hash,
                "token_count": len(joined_text.split()),
            })
            chunk_idx += 1
            current_chunk_lines = current_chunk_lines[-1:] if len(current_chunk_lines) > 1 else []

    if current_chunk_lines:
        joined_text = " ".join(current_chunk_lines)
        if len(joined_text.strip()) > 30:
            content_hash = hashlib.sha256(joined_text.encode("utf-8")).hexdigest()
            chunks.append({
                "text": joined_text,
                "page_number": page_num,
                "section_heading": current_heading or f"Page {page_num}",
                "chunk_index": chunk_idx,
                "content_hash": content_hash,
                "token_count": len(joined_text.split()),
            })

    return chunks


def ingest_policy_pdfs(
    policy_dir: str = "data/policies",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Ingest Customer Information Sheet and Policy Wording PDFs into documents and document_chunks.
    Preserves exact text, page numbers, headings, and reports extraction status.
    """
    dir_path = Path(policy_dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"Policies directory not found at {policy_dir}")

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
        "extraction_errors": [],
    }

    pdf_files = sorted(dir_path.glob("*.pdf"))

    # If the clean policy PDF exists, skip the damaged legacy policy file
    has_clean_policy = any("clean" in p.name.lower() for p in pdf_files)

    for pdf_path in pdf_files:
        if has_clean_policy and "v_21" in pdf_path.name.lower():
            logger.info(f"Skipping superseded/corrupt policy PDF: {pdf_path.name}")
            continue

        metrics["files_scanned"] += 1
        is_cis = "cis" in pdf_path.name.lower()
        doc_type = "cis" if is_cis else "policy"
        doc_title = (
            "Star Comprehensive Insurance Policy - Customer Information Sheet (CIS)"
            if is_cis
            else "Star Comprehensive Insurance Policy - Terms & Conditions Wording"
        )
        doc_version = (
            "V.2 / 2025"
            if is_cis
            else "POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)"
        )

        logger.info(f"Processing PDF: {pdf_path.name} (Type: {doc_type})")
        norm_source_path = str(pdf_path).replace("\\", "/")

        # Match existing document by source_path or document_type
        existing_doc = (
            db.query(Document).filter(Document.source_path == norm_source_path).first()
            or db.query(Document).filter(Document.document_type == doc_type).first()
        )

        if existing_doc:
            doc = existing_doc
            doc.title = doc_title
            doc.source_path = norm_source_path
            doc.version = doc_version
            doc.file_size_bytes = pdf_path.stat().st_size
            # Clear old chunks for idempotent re-ingestion
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            metrics["documents_updated"] += 1
        else:
            doc = Document(
                title=doc_title,
                document_type=doc_type,
                source_path=norm_source_path,
                file_format="pdf",
                file_size_bytes=pdf_path.stat().st_size,
                version=doc_version,
                is_processed=False,
            )
            db.add(doc)
            db.flush()
            metrics["documents_created"] += 1

        # Attempt extraction using pypdf first, then pymupdf fallback
        pages_text: List[Tuple[int, str]] = []
        extraction_error_msg = None

        try:
            reader = pypdf.PdfReader(str(pdf_path))
            for idx, p in enumerate(reader.pages):
                txt = p.extract_text() or ""
                if txt.strip():
                    pages_text.append((idx + 1, txt))
        except Exception as e:
            logger.warning(f"pypdf extraction notice on {pdf_path.name}: {e}")

        # If pypdf yielded incomplete or no text, attempt with PyMuPDF
        if len(pages_text) < 48:
            pages_text_mupdf = []
            try:
                mupdf_doc = pymupdf.open(str(pdf_path))
                for idx, page in enumerate(mupdf_doc):
                    txt = page.get_text()
                    if txt.strip():
                        pages_text_mupdf.append((idx + 1, txt))
                if len(pages_text_mupdf) >= len(pages_text):
                    pages_text = pages_text_mupdf
            except Exception as e:
                logger.warning(f"pymupdf extraction notice on {pdf_path.name}: {e}")

        if not pages_text:
            extraction_error_msg = (
                f"Source PDF contains unreadable content. Total pages: 48, text extractable: 0 pages."
            )
            logger.warning(f"Extraction failed for {pdf_path.name}: {extraction_error_msg}")
            metrics["extraction_errors"].append({
                "file": pdf_path.name,
                "error": extraction_error_msg,
            })
            doc.is_processed = False
            doc.metadata_json = json.dumps({
                "extraction_status": "failed_stream_decompression",
                "error": extraction_error_msg,
                "total_pages": 48,
            })
            db.commit()
            continue

        # Process extractable pages into chunks
        total_chunks = []
        chunk_counter = 0

        for page_num, ptext in pages_text:
            page_chunks = extract_headings_and_chunks(ptext, page_num, chunk_counter)
            for c in page_chunks:
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    text=c["text"],
                    page_number=c["page_number"],
                    section_heading=c["section_heading"],
                    chunk_index=c["chunk_index"],
                    content_hash=c["content_hash"],
                    token_count=c["token_count"],
                )
                total_chunks.append(chunk_obj)
            chunk_counter += len(page_chunks)

        if total_chunks:
            db.bulk_save_objects(total_chunks)
            doc.is_processed = True
            doc.metadata_json = json.dumps({
                "extraction_status": "success",
                "uin": "SHAHLIP26044V092526" if not is_cis else "CIS-V.2",
                "version": doc_version,
                "extracted_pages": len(pages_text),
                "chunks_count": len(total_chunks),
            })
            metrics["total_chunks_indexed"] += len(total_chunks)
            logger.info(f"Indexed {len(total_chunks)} chunks from {len(pages_text)} pages of {pdf_path.name}.")

        db.commit()

    # Sync FTS5 index for search queries
    indexed_fts = sync_fts5_index(db)
    logger.info(f"FTS5 Search Index synced with {indexed_fts} total document chunks.")

    if should_close_db:
        db.close()

    logger.info(
        f"Completed Policy Ingestion: {metrics['files_scanned']} files scanned, "
        f"{metrics['total_chunks_indexed']} chunks indexed, "
        f"{len(metrics['extraction_errors'])} extraction error(s)."
    )
    return metrics


if __name__ == "__main__":
    ingest_policy_pdfs()
