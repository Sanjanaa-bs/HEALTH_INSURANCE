"""
Evaluate Real Polynomial Hash Function & Vector Collisions

Analyzes the actual hash implementation in backend/app/services/embeddings.py:
  h = 0
  for char in token:
      h = (h * 31 + ord(char)) & 0xFFFFFFFF
  return h % vector_dim

Measures real collision rates and encoding latency across dimensions:
64, 128 (canonical default), 256, 512, 1024, 4096 on the corpus vocabulary
extracted directly from SQLite document_chunks.
"""

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RANDOM_SEED = 42

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

def polynomial_hash(token: str, vector_dim: int) -> int:
    h = 0
    for char in token:
        h = (h * 31 + ord(char)) & 0xFFFFFFFF
    return h % vector_dim

def run_collision_evaluation():
    db_path = Path("health_insurance.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT text FROM document_chunks")
    chunk_texts = [row[0] for row in c.fetchall()]
    conn.close()

    full_corpus = " ".join(chunk_texts).lower()

    # Extract corpus vocabulary
    words = re.findall(r"\b[a-z0-9]+\b", full_corpus)
    unique_words = sorted(list(set(w for w in words if len(w) >= 2)))

    # Bigrams
    unique_bigrams = set()
    for text in chunk_texts:
        t_words = re.findall(r"\b[a-z0-9]+\b", text.lower())
        for i in range(len(t_words) - 1):
            unique_bigrams.add(f"{t_words[i]}_{t_words[i+1]}")
    unique_bigrams = sorted(list(unique_bigrams))

    # 4-grams character subwords
    unique_4grams = set()
    for text in chunk_texts:
        clean = text.lower()
        for i in range(len(clean) - 3):
            sub = clean[i:i+4]
            if sub.strip():
                unique_4grams.add(sub)
    unique_4grams = sorted(list(unique_4grams))

    dimensions = [64, 128, 256, 512, 1024, 4096]
    ablation_results = {}

    print("\n" + "=" * 95)
    print(f"REAL POLYNOMIAL HASH COLLISION & LATENCY ANALYSIS (Corpus Vocab: {len(unique_words)} words)")
    print("=" * 95)
    print(f"{'DIM':<6} | {'WORD COLL (%)':<15} | {'BIGRAM COLL (%)':<16} | {'SUBWORD COLL (%)':<17} | {'CPU LATENCY (ms)':<16} | {'ZERO-DEPS'}")
    print("=" * 95)

    sample_texts = chunk_texts[:50]

    for dim in dimensions:
        # 1. Word collision
        word_buckets = set(polynomial_hash(w, dim) for w in unique_words)
        word_coll_rate = (1.0 - (len(word_buckets) / len(unique_words))) * 100.0

        # 2. Bigram collision
        bigram_buckets = set(polynomial_hash(b, dim) for b in unique_bigrams)
        bigram_coll_rate = (1.0 - (len(bigram_buckets) / len(unique_bigrams))) * 100.0

        # 3. Subword collision
        subword_buckets = set(polynomial_hash(s, dim) for s in unique_4grams)
        subword_coll_rate = (1.0 - (len(subword_buckets) / len(unique_4grams))) * 100.0

        # 4. Latency measurement (encode 50 passages)
        from backend.app.services.embeddings import LocalDenseEmbeddingProvider
        embedder = LocalDenseEmbeddingProvider(vector_dim=dim)
        t0 = time.perf_counter()
        for _ in range(5):
            for st in sample_texts:
                _ = embedder.embed_text(st)
        t1 = time.perf_counter()
        avg_latency_ms = ((t1 - t0) / (5 * len(sample_texts))) * 1000.0

        ablation_results[dim] = {
            "dimension": dim,
            "unique_words_count": len(unique_words),
            "word_collision_pct": round(word_coll_rate, 2),
            "unique_bigrams_count": len(unique_bigrams),
            "bigram_collision_pct": round(bigram_coll_rate, 2),
            "unique_subwords_count": len(unique_4grams),
            "subword_collision_pct": round(subword_coll_rate, 2),
            "latency_ms": round(avg_latency_ms, 4),
            "zero_dependencies": True,
        }

        print(f"{dim:<6} | {word_coll_rate:<15.2f} | {bigram_coll_rate:<16.2f} | {subword_coll_rate:<17.2f} | {avg_latency_ms:<16.4f} | Yes")

    print("=" * 95)

    # MiniLM latency comparison
    try:
        from sentence_transformers import SentenceTransformer
        m_model = SentenceTransformer("all-MiniLM-L6-v2")
        t0 = time.perf_counter()
        for st in sample_texts[:20]:
            _ = m_model.encode(st)
        t1 = time.perf_counter()
        minilm_latency_ms = ((t1 - t0) / 20.0) * 1000.0
    except Exception:
        minilm_latency_ms = None

    output_data = {
        "metadata": {
            "command": "python scripts/evaluate_embeddings_and_collisions.py",
            "git_commit": get_git_commit(),
            "date": datetime.now(timezone.utc).isoformat(),
            "random_seed": RANDOM_SEED,
            "hash_algorithm": "polynomial_mod (h * 31 + ord(char)) & 0xFFFFFFFF % dim",
            "corpus_chunks_count": len(chunk_texts),
            "minilm_cpu_latency_ms": round(minilm_latency_ms, 2) if minilm_latency_ms else "NOT RUN",
        },
        "vocabulary_stats": {
            "unique_words": len(unique_words),
            "unique_bigrams": len(unique_bigrams),
            "unique_4grams": len(unique_4grams),
        },
        "dimension_ablation": ablation_results,
    }

    out_file = Path("data/evaluation/embeddings_collision_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"Saved real collision evaluation results to {out_file}\n")

if __name__ == "__main__":
    run_collision_evaluation()
