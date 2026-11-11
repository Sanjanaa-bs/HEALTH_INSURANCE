"""
Information Retrieval Benchmark Evaluation (Real Data, Gold Chunks, Bootstrap 95% CIs)

Models evaluated:
1. Lexical BM25 (SQLite FTS5 via search_document_chunks)
2. Dense Feature Hashing (128-d LocalDenseEmbeddingProvider)
3. Dense MiniLM (Real sentence-transformers all-MiniLM-L6-v2)
4. Proposed Hybrid BM25 + Hash RRF (alpha=0.5)
5. Hybrid BM25 + MiniLM RRF (alpha=0.5)

Evaluated strictly on the 53 answerable benchmark questions against verified gold_chunk_ids.
"""

import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

# Ensure workspace root in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.search import search_document_chunks
from backend.app.services.embeddings import LocalDenseEmbeddingProvider, SentenceTransformersEmbeddingProvider
from backend.app.services.vector_store import LocalVectorStore

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

def compute_bootstrap_ci(scores: List[float], n_bootstraps: int = 1000, seed: int = 42) -> Dict[str, float]:
    if not scores:
        return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}
    rng = np.random.RandomState(seed)
    mean_val = float(np.mean(scores))
    boot_means = [float(np.mean(rng.choice(scores, size=len(scores), replace=True))) for _ in range(n_bootstraps)]
    return {
        "mean": round(mean_val, 4),
        "ci_lower": round(float(np.percentile(boot_means, 2.5)), 4),
        "ci_upper": round(float(np.percentile(boot_means, 97.5)), 4),
    }

def run_ir_evaluation():
    db = SessionLocal()
    benchmark_path = Path("data/evaluation/benchmark_qa_60.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    queries = benchmark_data["queries"] if isinstance(benchmark_data, dict) and "queries" in benchmark_data else benchmark_data
    # Filter answerable queries
    answerable_queries = [q for q in queries if q.get("expected_status") == "answered" and q.get("gold_chunk_ids")]
    print(f"Loaded {len(answerable_queries)} answerable benchmark queries.")

    # 1. Load Local Dense Vector Store (128-d)
    store_local = LocalVectorStore(filepath="vector_index.json")
    store_local.load()
    local_embedder = LocalDenseEmbeddingProvider(vector_dim=128)

    # 2. Load MiniLM Vector Store (384-d, real sentence-transformers)
    minilm_store_path = Path("vector_index_minilm.json")
    if not minilm_store_path.exists():
        print("Building vector_index_minilm.json with real sentence-transformers...")
        from scripts.index_embeddings import index_all_chunks
        index_all_chunks(db, provider_name="sentence-transformers", output_path="vector_index_minilm.json")

    store_minilm = LocalVectorStore(filepath="vector_index_minilm.json")
    store_minilm.load()
    minilm_embedder = SentenceTransformersEmbeddingProvider(model_name="all-MiniLM-L6-v2")

    systems = [
        "bm25",
        "hash_128_dense",
        "minilm_dense",
        "hybrid_bm25_hash_rrf",
        "hybrid_bm25_minilm_rrf",
    ]

    raw_scores = {s: {"P@1": [], "P@3": [], "P@5": [], "R@1": [], "R@3": [], "R@5": [], "MRR": [], "nDCG@5": []} for s in systems}

    def calc_ndcg_at_k(retrieved_ids: List[int], gold_set: set, k: int = 5) -> float:
        # Binary relevance: 1 if in gold_set else 0
        dcg = 0.0
        for rank, cid in enumerate(retrieved_ids[:k], 1):
            rel = 1.0 if cid in gold_set else 0.0
            dcg += (2.0**rel - 1.0) / math.log2(rank + 1)
        
        # Ideal DCG: top min(len(gold_set), k) are relevant
        idcg = sum((2.0**1.0 - 1.0) / math.log2(r + 1) for r in range(1, min(len(gold_set), k) + 1))
        return (dcg / idcg) if idcg > 0 else 0.0

    def compute_rrf_ranking(bm25_hits: List[int], vector_hits: List[int], alpha: float = 0.5, k_rrf: float = 60.0) -> List[int]:
        bm25_ranks = {cid: rank + 1 for rank, cid in enumerate(bm25_hits)}
        vector_ranks = {cid: rank + 1 for rank, cid in enumerate(vector_hits)}
        all_cids = set(bm25_ranks.keys()).union(set(vector_ranks.keys()))
        combined = []
        for cid in all_cids:
            s_bm25 = (alpha / (k_rrf + bm25_ranks[cid])) if cid in bm25_ranks else 0.0
            s_vec = ((1.0 - alpha) / (k_rrf + vector_ranks[cid])) if cid in vector_ranks else 0.0
            combined.append((cid, s_bm25 + s_vec))
        combined.sort(key=lambda x: x[1], reverse=True)
        return [cid for cid, _ in combined]

    for q in answerable_queries:
        q_text = q["question"]
        gold_set = set(q["gold_chunk_ids"])
        n_gold = len(gold_set)
        target_docs = q.get("target_documents", [])
        bm25_doc_type = target_docs[0] if len(target_docs) == 1 else None

        # 1. Lexical BM25
        bm25_res = search_document_chunks(db, q_text, document_type=bm25_doc_type, limit=20)
        bm25_ids = [r["chunk_id"] for r in bm25_res]

        # 2. Dense Hashed (128-d)
        q_hash_vec = local_embedder.embed_text(q_text)
        hash_res = store_local.search(q_hash_vec, top_k=20, document_type=target_docs)
        hash_ids = [r["chunk_id"] for r in hash_res]

        # 3. Dense MiniLM (384-d)
        q_minilm_vec = minilm_embedder.embed_text(q_text)
        minilm_res = store_minilm.search(q_minilm_vec, top_k=20, document_type=target_docs)
        minilm_ids = [r["chunk_id"] for r in minilm_res]

        # 4. Hybrid BM25 + Hash RRF
        hybrid_hash_ids = compute_rrf_ranking(bm25_ids, hash_ids, alpha=0.5)

        # 5. Hybrid BM25 + MiniLM RRF
        hybrid_minilm_ids = compute_rrf_ranking(bm25_ids, minilm_ids, alpha=0.5)

        system_retrievals = {
            "bm25": bm25_ids,
            "hash_128_dense": hash_ids,
            "minilm_dense": minilm_ids,
            "hybrid_bm25_hash_rrf": hybrid_hash_ids,
            "hybrid_bm25_minilm_rrf": hybrid_minilm_ids,
        }

        for sys_name, ret_ids in system_retrievals.items():
            # Precision@K
            p1 = 1.0 if (len(ret_ids) >= 1 and ret_ids[0] in gold_set) else 0.0
            p3 = (sum(1 for cid in ret_ids[:3] if cid in gold_set) / 3.0) if len(ret_ids) >= 3 else (sum(1 for cid in ret_ids[:3] if cid in gold_set) / max(1, len(ret_ids)))
            p5 = (sum(1 for cid in ret_ids[:5] if cid in gold_set) / 5.0) if len(ret_ids) >= 5 else (sum(1 for cid in ret_ids[:5] if cid in gold_set) / max(1, len(ret_ids)))

            # Recall@K
            r1 = (1.0 if (len(ret_ids) >= 1 and ret_ids[0] in gold_set) else 0.0) / n_gold
            r3 = sum(1 for cid in ret_ids[:3] if cid in gold_set) / n_gold
            r5 = sum(1 for cid in ret_ids[:5] if cid in gold_set) / n_gold

            # MRR
            mrr = 0.0
            for rank, cid in enumerate(ret_ids[:20], 1):
                if cid in gold_set:
                    mrr = 1.0 / rank
                    break

            # nDCG@5
            ndcg5 = calc_ndcg_at_k(ret_ids, gold_set, k=5)

            raw_scores[sys_name]["P@1"].append(p1)
            raw_scores[sys_name]["P@3"].append(p3)
            raw_scores[sys_name]["P@5"].append(p5)
            raw_scores[sys_name]["R@1"].append(r1)
            raw_scores[sys_name]["R@3"].append(r3)
            raw_scores[sys_name]["R@5"].append(r5)
            raw_scores[sys_name]["MRR"].append(mrr)
            raw_scores[sys_name]["nDCG@5"].append(ndcg5)

    db.close()

    # Aggregate with bootstrap 95% CIs
    aggregated_results = {}
    for sys_name, metrics in raw_scores.items():
        aggregated_results[sys_name] = {}
        for m_name, vals in metrics.items():
            aggregated_results[sys_name][m_name] = compute_bootstrap_ci(vals, n_bootstraps=1000, seed=RANDOM_SEED)

    output = {
        "metadata": {
            "command": "python scripts/evaluate_ir_metrics.py",
            "git_commit": get_git_commit(),
            "date": datetime.now(timezone.utc).isoformat(),
            "random_seed": RANDOM_SEED,
            "dataset_file": str(benchmark_path),
            "dataset_file_hash": get_file_hash(benchmark_path),
            "eval_queries_count": len(answerable_queries),
            "relevance_ground_truth": "binary exact gold_chunk_ids alignment",
        },
        "results": aggregated_results,
    }

    out_file = Path("data/evaluation/ir_metrics_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 105)
    print(f"INFORMATION RETRIEVAL BENCHMARK PERFORMANCE ({len(answerable_queries)} Answerable Queries)")
    print("=" * 105)
    print(f"{'SYSTEM':<26} | {'P@1':<8} | {'P@5':<8} | {'R@5':<8} | {'MRR':<8} | {'nDCG@5':<8} | 95% CI (MRR)")
    print("=" * 105)
    for sys_name, m in aggregated_results.items():
        p1 = m["P@1"]["mean"]
        p5 = m["P@5"]["mean"]
        r5 = m["R@5"]["mean"]
        mrr = m["MRR"]["mean"]
        ndcg = m["nDCG@5"]["mean"]
        ci_str = f"[{m['MRR']['ci_lower']:.4f}, {m['MRR']['ci_upper']:.4f}]"
        print(f"{sys_name:<26} | {p1:<8.4f} | {p5:<8.4f} | {r5:<8.4f} | {mrr:<8.4f} | {ndcg:<8.4f} | {ci_str}")
    print("=" * 105)
    print(f"Saved reproducible results to {out_file}\n")

if __name__ == "__main__":
    run_ir_evaluation()
