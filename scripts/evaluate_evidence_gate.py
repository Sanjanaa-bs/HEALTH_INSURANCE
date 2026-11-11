"""
Evaluate Evidence Gate Mechanisms Against Ground Truth

Evaluates evidence gating mechanisms at the passage level using the benchmark
ground truth in data/evaluation/benchmark_qa_60.json (53 answerable + 12 OOD = 65 queries).

Compares:
1. Old Gate (legacy substring matching)
2. New Gate (whole-word boundary regex + insurance query normalization)
3. Strict Gate (higher threshold: m >= 3 if |W| >= 3 else 2)
4. Cosine Gate (real SentenceTransformer all-MiniLM-L6-v2 with threshold tau = 0.45)
5. Hybrid Gate (keyword match >= 1 and MiniLM cosine >= 0.35)

Outputs real passage-level Precision, Recall, F1, Distractor Rejection Rate,
and Out-of-Domain (N=12) Query Abstention Rate to data/evaluation/evidence_gate_results.json.
"""

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Set
import numpy as np

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.search import search_document_chunks, normalize_insurance_query_text
from backend.app.services.qa import extract_meaningful_keywords
from sentence_transformers import SentenceTransformer

RANDOM_SEED = 42

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_evidence_gate_evaluation():
    db = SessionLocal()
    benchmark_path = Path("data/evaluation/benchmark_qa_60.json")
    benchmark_hash = compute_file_sha256(benchmark_path)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    queries = benchmark_data["queries"]
    print(f"Loaded {len(queries)} queries from {benchmark_path} (SHA-256: {benchmark_hash[:12]}...)")

    # Load MiniLM model
    print("Loading SentenceTransformer all-MiniLM-L6-v2 for semantic cosine gate...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    gate_names = [
        "old_gate_substring",
        "new_gate_word_boundary",
        "strict_gate_m3",
        "cosine_gate_minilm_tau45",
        "hybrid_gate_kw_minilm",
    ]

    # Passage-level tracking
    # TP: Gate accepts passage AND passage is gold
    # FP: Gate accepts passage AND passage is NOT gold (distractor or OOD)
    # TN: Gate rejects passage AND passage is NOT gold
    # FN: Gate rejects passage AND passage is gold
    passage_stats = {g: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for g in gate_names}

    # Query-level tracking for OOD (N=12) and Answerable (N=53)
    ood_query_total = 0
    ood_abstained = {g: 0 for g in gate_names}

    answerable_query_total = 0
    answerable_accepted = {g: 0 for g in gate_names}

    # Distractor passage tracking (retrieved passages for answerable queries that are NOT gold)
    distractor_passage_total = 0
    distractor_passage_rejected = {g: 0 for g in gate_names}

    # Pre-fetch candidate embeddings caching for efficiency
    for q_idx, q_item in enumerate(queries):
        qid = q_item["id"]
        q_text = q_item["question"]
        is_ood = q_item.get("expected_status") == "insufficient_evidence"
        gold_ids = set(q_item.get("gold_chunk_ids", []))

        if is_ood:
            ood_query_total += 1
        else:
            answerable_query_total += 1

        # Retrieve top-5 candidate passages from BM25
        candidates = search_document_chunks(db=db, query_text=q_text, limit=5)

        # Precompute query representations
        kw_legacy = extract_meaningful_keywords(q_text, legacy=True)
        kw_new = extract_meaningful_keywords(q_text, legacy=False)
        q_emb = model.encode(q_text, convert_to_numpy=True)
        q_norm = np.linalg.norm(q_emb)
        if q_norm > 1e-6:
            q_emb = q_emb / q_norm

        # Track which gates accepted at least one passage for this query
        query_has_accepted_passage = {g: False for g in gate_names}

        for cand in candidates:
            chunk_id = cand["chunk_id"]
            is_gold = (chunk_id in gold_ids) if not is_ood else False

            if not is_ood and not is_gold:
                distractor_passage_total += 1

            full_c = (f"{cand.get('section_heading', '')} {cand.get('full_text', '')} {cand.get('supporting_text', '')} {cand.get('excerpt', '')}").lower()
            norm_c = normalize_insurance_query_text(full_c)

            # 1. Old Gate (substring)
            req_old = 2 if len(kw_legacy) >= 3 else 1
            hits_old = sum(1 for w in kw_legacy if w in full_c)
            pass_old = (hits_old >= req_old)

            # 2. New Gate (word-boundary regex + normalization)
            req_new = 2 if len(kw_new) >= 3 else 1
            hits_new = sum(1 for w in kw_new if re.search(rf"\b{re.escape(w)}\b", norm_c))
            pass_new = (hits_new >= req_new)

            # 3. Strict Gate (m >= 3 if |W| >= 3 else 2)
            req_strict = 3 if len(kw_new) >= 3 else 2
            hits_strict = sum(1 for w in kw_new if re.search(rf"\b{re.escape(w)}\b", norm_c))
            pass_strict = (hits_strict >= req_strict)

            # 4. Cosine Gate with real MiniLM (tau = 0.45)
            # Encode chunk text
            cand_text = f"{cand.get('section_heading', '')}. {cand.get('supporting_text', '') or cand.get('full_text', '')}"
            cand_emb = model.encode(cand_text, convert_to_numpy=True)
            cand_norm = np.linalg.norm(cand_emb)
            if cand_norm > 1e-6:
                cand_emb = cand_emb / cand_norm
            sim = float(np.dot(q_emb, cand_emb))
            pass_cosine = (sim >= 0.45)

            # 5. Hybrid Gate (kw hits >= 1 and cosine >= 0.35)
            pass_hybrid = (hits_new >= 1 and sim >= 0.35)

            decisions = {
                "old_gate_substring": pass_old,
                "new_gate_word_boundary": pass_new,
                "strict_gate_m3": pass_strict,
                "cosine_gate_minilm_tau45": pass_cosine,
                "hybrid_gate_kw_minilm": pass_hybrid,
            }

            for g in gate_names:
                accepted = decisions[g]
                if accepted:
                    query_has_accepted_passage[g] = True

                # Passage-level confusion matrix
                if is_gold:
                    if accepted:
                        passage_stats[g]["TP"] += 1
                    else:
                        passage_stats[g]["FN"] += 1
                else:
                    if accepted:
                        passage_stats[g]["FP"] += 1
                    else:
                        passage_stats[g]["TN"] += 1
                        if not is_ood:
                            distractor_passage_rejected[g] += 1

        # Query-level updates
        for g in gate_names:
            if is_ood:
                if not query_has_accepted_passage[g]:
                    ood_abstained[g] += 1
            else:
                if query_has_accepted_passage[g]:
                    answerable_accepted[g] += 1

    db.close()

    # Compute metrics
    metrics = {}
    print("\n" + "=" * 105)
    print(f"EVIDENCE GATE COMPARATIVE EVALUATION (N={len(queries)} queries: {answerable_query_total} in-domain, {ood_query_total} OOD)")
    print("=" * 105)
    print(f"{'MECHANISM':<25} | {'PREC':<6} | {'REC':<6} | {'F1':<6} | {'SPEC':<6} | {'FAR':<6} | {'DIST REJ %':<11} | {'OOD ABSTAIN %'}")
    print("=" * 105)

    for g in gate_names:
        st = passage_stats[g]
        tp, fp, tn, fn = st["TP"], st["FP"], st["TN"], st["FN"]

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        far = fp / (tn + fp) if (tn + fp) > 0 else 0.0
        frr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

        dist_rej_pct = (distractor_passage_rejected[g] / distractor_passage_total * 100.0) if distractor_passage_total > 0 else 0.0
        ood_abstain_pct = (ood_abstained[g] / ood_query_total * 100.0) if ood_query_total > 0 else 0.0
        ans_accept_pct = (answerable_accepted[g] / answerable_query_total * 100.0) if answerable_query_total > 0 else 0.0

        metrics[g] = {
            "passage_confusion_matrix": st,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "specificity": round(spec, 4),
            "false_acceptance_rate": round(far, 4),
            "false_rejection_rate": round(frr, 4),
            "distractor_passages": {
                "total": distractor_passage_total,
                "rejected": distractor_passage_rejected[g],
                "rejection_rate_pct": round(dist_rej_pct, 2),
            },
            "ood_abstention": {
                "total_queries": ood_query_total,
                "abstained_queries": ood_abstained[g],
                "abstention_rate_pct": round(ood_abstain_pct, 2),
            },
            "answerable_coverage": {
                "total_queries": answerable_query_total,
                "accepted_queries": answerable_accepted[g],
                "coverage_pct": round(ans_accept_pct, 2),
            },
        }

        print(f"{g:<25} | {prec:<6.4f} | {rec:<6.4f} | {f1:<6.4f} | {spec:<6.4f} | {far:<6.4f} | {dist_rej_pct:<11.1f} | {ood_abstain_pct:.1f}%")

    print("=" * 105)

    output_data = {
        "metadata": {
            "command": "python scripts/evaluate_evidence_gate.py",
            "git_commit": get_git_commit(),
            "date": datetime.now(timezone.utc).isoformat(),
            "random_seed": RANDOM_SEED,
            "benchmark_file": "data/evaluation/benchmark_qa_60.json",
            "benchmark_sha256": benchmark_hash,
            "total_queries": len(queries),
            "answerable_queries": answerable_query_total,
            "ood_queries": ood_query_total,
            "distractor_passages_evaluated": distractor_passage_total,
            "candidate_retrieval_limit": 5,
        },
        "gates": metrics,
    }

    out_file = Path("data/evaluation/evidence_gate_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved real evidence gate evaluation to {out_file}\n")

if __name__ == "__main__":
    run_evidence_gate_evaluation()
