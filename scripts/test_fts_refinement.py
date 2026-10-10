import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

STOPWORDS = {
    "what", "is", "the", "for", "are", "about", "does", "say", "to", "of",
    "in", "and", "a", "an", "policy", "tell", "me", "how", "can", "do",
    "it", "any", "which", "with", "from", "on", "under", "this", "that",
    "these", "those", "have", "has", "had", "be", "been", "being", "there"
}

questions = [
    "What is the waiting period for pre-existing diseases?",
    "What does the policy say about room rent?",
    "Are cataract treatments subject to specific conditions?",
    "What does the policy say about pre-hospitalisation expenses?",
    "What are the policy's exclusions?",
    "What is the policy for orbital space flight and planetary excursion?"
]

for q in questions:
    words = re.findall(r"\b[a-zA-Z0-9]+\b", q)
    content_words = [w for w in words if w.lower() not in STOPWORDS]
    if not content_words:
        content_words = words

    q_and = " AND ".join([f'"{w}"' for w in content_words])
    sql_and = text("""
        SELECT c.id, c.page_number, c.section_heading, d.title, snippet(document_chunks_fts, 2, '[', ']', '...', 12)
        FROM document_chunks_fts
        JOIN document_chunks c ON c.id = document_chunks_fts.chunk_id
        JOIN documents d ON d.id = c.document_id
        WHERE document_chunks_fts MATCH :q
        ORDER BY rank
        LIMIT 2;
    """)
    rows = db.execute(sql_and, {"q": q_and}).fetchall()

    if not rows and len(content_words) > 1:
        q_or = " OR ".join([f'"{w}"' for w in content_words])
        rows = db.execute(sql_and, {"q": q_or}).fetchall()

    print("========================================")
    print("Q:", q)
    print("  Keywords:", content_words)
    print("  Matches found:", len(rows))
    for r in rows:
        print(f"  Match: Page {r[1]} | Section: {r[2]}")
        print(f"    Snippet: {r[4]}")
    if not rows:
        print("  Abstention: 0 matches found.")

db.close()
