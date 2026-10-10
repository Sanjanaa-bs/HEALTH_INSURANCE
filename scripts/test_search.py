import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.search import search_document_chunks

def test_queries():
    db = SessionLocal()
    queries = [
        "cataract",
        "waiting period",
        "room rent",
        "pre-hospitalization",
        "maternity",
        "exclusions",
        "cashless claims",
    ]
    print("=== SEARCH FUNCTIONALITY VERIFICATION ===")

    for q in queries:
        print(f"\nQuery: '{q}'")
        results = search_document_chunks(db=db, query_text=q, limit=3)
        print(f"  Total results returned: {len(results)}")
        for idx, r in enumerate(results, 1):
            title = r['document_title'].encode('ascii', errors='backslashreplace').decode('ascii')
            heading = str(r['section_heading']).encode('ascii', errors='backslashreplace').decode('ascii')
            excerpt = r['excerpt'].encode('ascii', errors='backslashreplace').decode('ascii')[:150]
            print(f"  [{idx}] Doc: '{title}' ({r['document_type']}) | Page: {r['page_number']} | Section: '{heading}'")
            print(f"      Excerpt: '{excerpt}'")

    db.close()

if __name__ == "__main__":
    test_queries()
