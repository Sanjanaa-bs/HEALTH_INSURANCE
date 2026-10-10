import sys
from pathlib import Path

# Ensure root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

queries = [
    {
        "question": "What is the waiting period for pre-existing diseases?",
        "query": "waiting period pre-existing diseases",
    },
    {
        "question": "What does the policy say about room rent?",
        "query": "room rent",
    },
    {
        "question": "Are cataract treatments subject to specific conditions?",
        "query": "cataract",
    },
    {
        "question": "What does the policy say about pre-hospitalisation expenses?",
        "query": "pre-hospitalization expenses",
    },
    {
        "question": "What are the policy's exclusions?",
        "query": "exclusions",
    },
    {
        "question": "What is the policy for orbital space flight and planetary excursion?",
        "query": "orbital space flight planetary excursion",
    },
]

print("=== END-TO-END SEARCH RETRIEVAL & CITATION AUDIT ===\n")

for item in queries:
    q_text = item["question"]
    search_q = item["query"]
    resp = client.get(f"/api/v1/documents/search?q={search_q}")
    assert resp.status_code == 200, f"Status {resp.status_code}"
    data = resp.json()
    results = data.get("results", [])

    print(f"QUESTION: {q_text}")
    print(f"API Search Query: '{search_q}'")
    print(f"Total Results Found: {len(results)}")

    if not results:
        print("RESULT: Abstention / No evidence found.")
        print("EVIDENCE: 0 matching passages returned by search index. System does not invent details.\n")
        continue

    for i, r in enumerate(results[:2], 1):
        clean_excerpt = r["excerpt"].replace("<b>", "").replace("</b>", "").strip()
        print(f"  Citation [{i}]:")
        print(f"    Document: {r['document_title']} ({r['document_type']})")
        print(f"    Page: Physical Page {r['page_number']}")
        print(f"    Section: {r['section_heading']}")
        print(f"    Passage: {clean_excerpt[:150]}...")
    print()
