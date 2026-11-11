"""
Align Benchmark Questions with Real Database Chunks to Establish Ground Truth
"""

import json
import sqlite3
from pathlib import Path

def align_gold_chunks():
    benchmark_path = Path("data/evaluation/benchmark_qa_60.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If it was a list or dict with queries
    queries = data["queries"] if isinstance(data, dict) and "queries" in data else data

    conn = sqlite3.connect("health_insurance.db")
    c = conn.cursor()

    # Load all 263 chunks
    c.execute("""
        SELECT c.id, d.document_type, c.page_number, c.section_heading, c.text
        FROM document_chunks c
        JOIN documents d ON c.document_id = d.id
    """)
    all_chunks = c.fetchall()
    conn.close()

    total_answerable = 0
    total_ood = 0
    missing_gold = []

    # Explicit verified mappings for edge cases
    explicit_gold_mapping = {
        "Q13": [96, 5],    # Modern Treatments / Robotic Surgery (Policy p.10 sec.4, CIS p.3 sec.II.6)
        "Q15": [121, 9],   # Health Checkup (Policy p.16 sec.18, CIS p.4 sec.II.18)
        "Q23": [116, 8],   # Coverage for New Born Baby (Policy p.15 sec.15, CIS p.4 sec.II.15)
        "Q24": [124, 9],   # Mental Illness (Policy p.17 sec.22, CIS p.4 sec.II.22)
        "Q25": [129],      # Buy Back Pre-Existing Disease (Policy p.19 sec.27)
        "Q48": [207, 226], # Portability (Policy p.44, FAQ p.2)
        "Q49": [240, 18],  # Cashless process & non-payable deductions (Claim Guidance chunk 240, CIS p.6)
    }

    for q in queries:
        is_ood = (q.get("expected_status") == "insufficient_evidence")
        if is_ood:
            total_ood += 1
            q["gold_chunk_ids"] = []
            q["gold_passages"] = []
            continue

        total_answerable += 1
        q_id = q["id"]

        if q_id in explicit_gold_mapping:
            gold_ids = explicit_gold_mapping[q_id]
            gold_passages = []
            for cid, doc_type, pg, heading, text in all_chunks:
                if cid in gold_ids:
                    gold_passages.append({
                        "chunk_id": cid,
                        "document_type": doc_type,
                        "page_number": pg,
                        "section_heading": heading,
                        "snippet": text[:180].strip() + "..."
                    })
            q["gold_chunk_ids"] = gold_ids
            q["gold_passages"] = gold_passages
            continue

        target_docs = set(q.get("target_documents", []))
        exp_pages = set(q.get("expected_page_numbers", []))
        key_phrases = [kp.lower() for kp in q.get("key_phrases", [])]

        gold_ids = []
        gold_passages = []

        for cid, doc_type, pg, heading, text in all_chunks:
            if doc_type in target_docs and pg in exp_pages:
                full_t = f"{heading or ''} {text}".lower()
                # Check if at least one key phrase is present in this chunk
                matches = [kp for kp in key_phrases if kp in full_t]
                if matches:
                    gold_ids.append(cid)
                    # Excerpt
                    gold_passages.append({
                        "chunk_id": cid,
                        "document_type": doc_type,
                        "page_number": pg,
                        "section_heading": heading,
                        "snippet": text[:180].strip() + "..."
                    })

        # Fallback: if strict page match yielded none, search across target docs for multiple key phrases
        if not gold_ids:
            for cid, doc_type, pg, heading, text in all_chunks:
                if doc_type in target_docs:
                    full_t = f"{heading or ''} {text}".lower()
                    matches = [kp for kp in key_phrases if kp in full_t]
                    if len(matches) >= 2:
                        gold_ids.append(cid)
                        gold_passages.append({
                            "chunk_id": cid,
                            "document_type": doc_type,
                            "page_number": pg,
                            "section_heading": heading,
                            "snippet": text[:180].strip() + "..."
                        })

        q["gold_chunk_ids"] = gold_ids
        q["gold_passages"] = gold_passages

        if not gold_ids:
            missing_gold.append(q["id"])

    output_data = {
        "metadata": {
            "authorship": "Authored by paper authors; independent validation pending",
            "validation_status": "authored_pending_human_audit",
            "total_queries": len(queries),
            "answerable_queries": total_answerable,
            "out_of_domain_queries": total_ood,
            "indexed_database_chunks": len(all_chunks)
        },
        "queries": queries
    }

    with open(benchmark_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Aligned benchmark: {len(queries)} queries ({total_answerable} answerable, {total_ood} OOD).")
    if missing_gold:
        print(f"WARNING: Missing gold chunks for: {missing_gold}")
    else:
        print("All 53 answerable queries successfully mapped to real database gold chunks!")

if __name__ == "__main__":
    align_gold_chunks()
