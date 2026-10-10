import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, or_

from backend.app.models.document import Document, DocumentChunk

logger = logging.getLogger("document_search")


def init_fts5_table(db: Session) -> bool:
    """Initialize SQLite FTS5 full-text virtual table for document chunks."""
    try:
        db.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
                chunk_id UNINDEXED,
                document_id UNINDEXED,
                text,
                section_heading,
                tokenize = 'porter unicode61'
            );
        """))
        db.commit()
        return True
    except Exception as e:
        logger.warning(f"SQLite FTS5 initialization notice: {e}")
        db.rollback()
        return False


def sync_fts5_index(db: Session) -> int:
    """Populate or sync FTS5 virtual table from current document_chunks."""
    if not init_fts5_table(db):
        return 0

    try:
        # Clear existing FTS index
        db.execute(text("DELETE FROM document_chunks_fts;"))
        # Populate from document_chunks
        result = db.execute(text("""
            INSERT INTO document_chunks_fts (chunk_id, document_id, text, section_heading)
            SELECT id, document_id, text, COALESCE(section_heading, '')
            FROM document_chunks;
        """))
        db.commit()
        count = db.execute(text("SELECT count(*) FROM document_chunks_fts;")).scalar() or 0
        logger.info(f"Synchronized FTS5 index with {count} chunks.")
        return count
    except Exception as e:
        logger.error(f"FTS5 sync failed: {e}")
        db.rollback()
        return 0


def generate_excerpt(text_content: str, query: str, max_chars: int = 250) -> str:
    """Generate a readable snippet centered around query term."""
    q_words = [re.escape(w) for w in query.split() if len(w) > 2]
    if not q_words:
        return text_content[:max_chars] + ("..." if len(text_content) > max_chars else "")

    pattern = re.compile(rf"({'|'.join(q_words)})", re.IGNORECASE)
    match = pattern.search(text_content)
    if not match:
        return text_content[:max_chars] + ("..." if len(text_content) > max_chars else "")

    start = max(0, match.start() - 80)
    end = min(len(text_content), match.end() + 150)
    snippet = text_content[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(text_content):
        snippet = snippet + "..."

    return pattern.sub(r"<b>\1</b>", snippet)


def format_page_label(doc_type: str, page_number: Optional[int]) -> tuple:
    """Return (printed_page_number, formatted_page_label) for citations."""
    if page_number is None:
        return None, None
    if doc_type == "policy":
        if page_number == 1:
            return None, "Physical Page 1 (Cover Page)"
        printed = page_number - 1
        return printed, f"Physical Page {page_number} (Printed Page {printed}/47)"
    elif doc_type == "cis":
        if page_number == 1:
            return None, "Physical Page 1 (Cover / Header)"
        printed = page_number - 1
        return printed, f"Physical Page {page_number} (Printed Page {printed}/19)"
    return page_number, f"Page {page_number}"


QUERY_STOPWORDS = {
    "what", "is", "the", "for", "are", "about", "does", "say", "to", "of",
    "in", "and", "a", "an", "policy", "tell", "me", "how", "can", "do",
    "it", "any", "which", "with", "from", "on", "under", "this", "that",
    "these", "those", "have", "has", "had", "be", "been", "being", "there",
    "cover", "covered", "coverage", "says", "mean", "means", "give", "gives",
    "before", "after", "related", "terms", "term", "high", "low", "provide",
    "provides", "provided", "details", "detail"
}

SPELLING_VARIANTS = {
    "hospitalisation": "hospitalization",
    "prehospitalisation": "prehospitalization",
    "organisation": "organization",
    "authorisation": "authorization",
}


def normalize_query_words(raw_query: str) -> List[str]:
    """Extract and normalize meaningful search tokens from natural language query."""
    expanded_query = raw_query.lower()
    # Expand conversational pre- and post-hospitalisation phrases to standard insurance terms
    expanded_query = re.sub(r"\b(before|prior to)\s+(hospitali[sz]ation)\b", "pre hospitalization", expanded_query)
    expanded_query = re.sub(r"\b(after|post|following)\s+(hospitali[sz]ation)\b", "post hospitalization", expanded_query)

    raw_tokens = re.findall(r"\b[a-zA-Z0-9]+\b", expanded_query)
    cleaned = []
    for t in raw_tokens:
        lower_t = t.lower()
        if len(lower_t) <= 1 or lower_t == "s":
            continue
        normalized = SPELLING_VARIANTS.get(lower_t, lower_t)
        cleaned.append(normalized)
    
    meaningful = [w for w in cleaned if w not in QUERY_STOPWORDS]
    return meaningful if meaningful else cleaned


def search_document_chunks(
    db: Session,
    query_text: str,
    document_type: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search document passages using SQLite FTS5 with BM25 ranking.
    Uses token normalization with multi-tier AND/OR matching.
    Falls back gracefully to multi-keyword ILIKE query if FTS5 is unindexed or encounters syntax issues.
    """
    cleaned_query = query_text.strip()
    if not cleaned_query:
        return []

    tokens = normalize_query_words(cleaned_query)
    if not tokens:
        return []

    results = []

    # Attempt FTS5 query first
    try:
        fts_sql = text("""
            SELECT 
                c.id, c.document_id, c.text, c.page_number, c.section_heading, c.content_hash,
                d.title as doc_title, d.document_type as doc_type,
                snippet(document_chunks_fts, 2, '<b>', '</b>', '...', 32) as snippet_text,
                bm25(document_chunks_fts) as rank,
                d.version as doc_version
            FROM document_chunks_fts
            JOIN document_chunks c ON c.id = document_chunks_fts.chunk_id
            JOIN documents d ON d.id = c.document_id
            WHERE document_chunks_fts MATCH :query
              AND (:doc_type IS NULL OR d.document_type = :doc_type)
            ORDER BY rank
            LIMIT :limit;
        """)

        # Tier 1: Try strict AND match across all meaningful tokens
        q_and = " AND ".join([f'"{w}"' for w in tokens])
        rows = db.execute(
            fts_sql,
            {"query": q_and, "doc_type": document_type, "limit": limit},
        ).fetchall()

        # Tier 2: If AND returned fewer than limit and multiple tokens exist, try OR with BM25 ranking
        if len(rows) < limit and len(tokens) > 1:
            q_or = " OR ".join([f'"{w}"' for w in tokens])
            or_rows = db.execute(
                fts_sql,
                {"query": q_or, "doc_type": document_type, "limit": limit},
            ).fetchall()
            existing_ids = {r[0] for r in rows}
            for r in or_rows:
                if r[0] not in existing_ids:
                    rows.append(r)
                    existing_ids.add(r[0])
                    if len(rows) >= limit:
                        break

        for r in rows:
            doc_t = r[7]
            pg_num = r[3]
            doc_ver = r[10] if len(r) > 10 else None
            printed_pg, page_lbl = format_page_label(doc_t, pg_num)
            results.append({
                "chunk_id": r[0],
                "document_id": r[1],
                "document_title": r[6],
                "document_type": doc_t,
                "version": doc_ver,
                "page_number": pg_num,
                "printed_page_number": printed_pg,
                "page_label": page_lbl,
                "section_heading": r[4],
                "excerpt": r[8] or generate_excerpt(r[2], cleaned_query),
                "full_text": r[2],
                "content_hash": r[5],
            })

        if results:
            return results
    except Exception as e:
        logger.debug(f"FTS5 query attempt bypassed: {e}")

    # Fallback search using tokenized matching across text and section headings
    query = db.query(DocumentChunk).join(Document)
    if document_type:
        query = query.filter(Document.document_type == document_type.strip().lower())

    all_chunks = query.all()
    ranked_chunks = []
    for c in all_chunks:
        full_haystack = f"{c.section_heading or ''} {c.text}".lower()
        match_count = sum(1 for t in tokens if t in full_haystack)
        if match_count > 0:
            ranked_chunks.append((match_count, c))

    ranked_chunks.sort(key=lambda x: x[0], reverse=True)
    matched_chunks = [c for _, c in ranked_chunks[:limit]]

    for c in matched_chunks:
        doc_t = c.document.document_type if c.document else "unknown"
        doc_ver = c.document.version if c.document else None
        printed_pg, page_lbl = format_page_label(doc_t, c.page_number)
        results.append({
            "chunk_id": c.id,
            "document_id": c.document_id,
            "document_title": c.document.title if c.document else "Document",
            "document_type": doc_t,
            "version": doc_ver,
            "page_number": c.page_number,
            "printed_page_number": printed_pg,
            "page_label": page_lbl,
            "section_heading": c.section_heading,
            "excerpt": generate_excerpt(c.text, cleaned_query),
            "full_text": c.text,
            "content_hash": c.content_hash,
        })

    return results
