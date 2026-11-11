# Evaluation Audit & Traceability Matrix

**Conference:** International Conference on Intelligent Computing and Future Technologies (ICICF-2027)  
**Host:** JAIN (Deemed-to-be University), Bengaluru, India  
**Paper ID:** 907  
**Title:** *An Offline-Capable Intelligent Assistant for Cashless Hospital Verification and Policy Clause Retrieval*  
**Branch:** `revision-honest-eval`  
**Base Commit:** `7fc8e410687f5b2753a2ad97b4b555bfd7eed753`  
**Audit Date:** 2026-11-11  

---

## 1. Non-Negotiable Scientific Integrity Principles

This audit document establishes complete traceability for every numerical claim, table entry, and benchmark result in the ICICF-2027 camera-ready paper (`docs/camera_ready_paper.tex`), revised manuscript (`docs/REVISED_RESEARCH_PAPER_ICICF2027.md`), and response to reviewers (`docs/RESPONSE_TO_REVIEWERS.md`).

1. **Zero Fabrication**: No simulated, estimated, hardcoded, or illustrative numbers are used. Every value is derived directly from an executed Python script operating on real data.
2. **True System Naming**: All systems are named strictly for what they are. Neural dense evaluations use real `sentence-transformers all-MiniLM-L6-v2`. Feature hashing is identified as polynomial subword feature hashing. If a component was offline (e.g., local Ollama LLM), it is strictly marked as `[NOT RUN - Local LLM offline]` without synthetic substitution.
3. **Explicit Labeling of Synthetic Data**: All synthetic data (`data/synthetic/synthetic_hospital_stress_sample.json`) is strictly labeled as synthetic stress-testing data and never described as verified insurer records.
4. **Honest Reporting of Parity and Negative Results**: Parity between BM25 and neural hybrid models on formal statutory text is reported objectively, and the performance limitations of polynomial feature hashing are documented transparently.
5. **Human Evaluation Transparency**: Benchmark authorship is clearly documented as author-prepared, and generation quality rating fields are reserved as `[Pending Human Rating]` referencing double-blind rating sheets (`data/evaluation/generation_quality_human_rating_sheet.csv`).

---

## 2. Master Number-to-Script Traceability Matrix

| Table / Section | Paper Claim | Measured Real Value | Script | Output JSON Artifact | Commit | Seed | Dataset & Hash |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Abstract / Table II** | Active Corpus Size | **263 chunks** (7 docs) | `scripts/index_embeddings.py` | `data/policies/manifest.json` | `7fc8e41` | 42 | `data/policies/` (`3 PDFs, 4 MHTML`) |
| **Table IV: BM25** | P@1 / P@5 / R@5 | **0.2830 / 0.2113 / 0.4241** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: BM25** | MRR / nDCG@5 | **0.4379 / 0.3537** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hash-128** | P@1 / P@5 / R@5 | **0.1132 / 0.0943 / 0.1713** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hash-128** | MRR / nDCG@5 | **0.2187 / 0.1415** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: MiniLM** | P@1 / P@5 / R@5 | **0.2453 / 0.1660 / 0.2747** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: MiniLM** | MRR / nDCG@5 | **0.3648 / 0.2665** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hybrid Hash** | P@1 / P@5 / R@5 | **0.2453 / 0.1736 / 0.3230** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hybrid Hash** | MRR / nDCG@5 | **0.3750 / 0.2779** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hybrid MiniLM** | P@1 / P@5 / R@5 | **0.2830 / 0.2226 / 0.4088** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table IV: Hybrid MiniLM** | MRR / nDCG@5 | **0.4243 / 0.3499** | `scripts/evaluate_ir_metrics.py` | `data/evaluation/ir_metrics_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table V: Hash Collisions** | Word Coll. Rate ($d=128$) | **95.94%** (3,155 words) | `scripts/evaluate_embeddings_and_collisions.py` | `data/evaluation/embeddings_collision_results.json` | `7fc8e41` | 42 | `health_insurance.db` (`document_chunks`) |
| **Table V: Hash Collisions** | Bigram Coll. Rate ($d=128$) | **99.00%** (12,786 bigrams) | `scripts/evaluate_embeddings_and_collisions.py` | `data/evaluation/embeddings_collision_results.json` | `7fc8e41` | 42 | `health_insurance.db` (`document_chunks`) |
| **Table V: Hash Collisions** | Subword Coll. ($d=128$) | **99.38%** (20,593 4-grams) | `scripts/evaluate_embeddings_and_collisions.py` | `data/evaluation/embeddings_collision_results.json` | `7fc8e41` | 42 | `health_insurance.db` (`document_chunks`) |
| **Table V: Latency** | Hash CPU Latency ($d=128$) | **0.8237 ms** | `scripts/evaluate_embeddings_and_collisions.py` | `data/evaluation/embeddings_collision_results.json` | `7fc8e41` | 42 | 50 sample chunks, 5 trials |
| **Table V: Latency** | MiniLM CPU Latency | **65.33 ms** | `scripts/evaluate_embeddings_and_collisions.py` | `data/evaluation/embeddings_collision_results.json` | `7fc8e41` | 42 | 20 sample chunks, CPU |
| **Table VI: Old Gate** | Prec / Recall / F1 | **0.2054 / 0.9464 / 0.3376** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: Old Gate** | Dist. Rej / OOD Abst. | **15.8% / 25.0%** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: New Gate** | Prec / Recall / F1 | **0.2208 / 0.9464 / 0.3581** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: New Gate** | Dist. Rej / OOD Abst. | **20.6% / 41.7%** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: Strict Gate** | Prec / Recall / F1 | **0.2384 / 0.6429 / 0.3478** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: Strict Gate** | Dist. Rej / OOD Abst. | **46.9% / 75.0%** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: Cosine Gate** | Prec / Recall / F1 | **0.2519 / 0.6071 / 0.3560** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VI: Cosine Gate** | Dist. Rej / OOD Abst. | **52.6% / 83.3%** | `scripts/evaluate_evidence_gate.py` | `data/evaluation/evidence_gate_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Extractive Answerable Cov. | **51 / 53 (96.2%)** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Extractive OOD Abstention | **6 / 12 (50.0%)** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Gold Chunk Precision | **35 / 132 (26.5%)** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Expected Page Precision | **50 / 132 (37.9%)** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Key Phrase Recall | **91 / 171 (53.2%)** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | `benchmark_qa_60.json` (`36a55b2d2280...`) |
| **Table VII: Generation** | Grounding / Hallucination | **100% Verbatim / 0% Halluc.** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | Extractive synthesis by construction |
| **Table VII: Generation** | Local LLM Status | **[NOT RUN - LLM offline]** | `scripts/evaluate_generation_quality.py` | `data/evaluation/generation_quality_results.json` | `7fc8e41` | 42 | Ollama offline at 11434 |
| **Table VIII: Matcher** | Dev Set Acc / Prec / Rec | **1.0000 / 1.0000 / 1.0000** | `scripts/evaluate_hospital_matcher_extended.py` | `data/evaluation/hospital_matcher_results.json` | `7fc8e41` | 42 | Dev pairs ($N=30$, seed 42) |
| **Table VIII: Matcher** | Test Set Acc / Prec / Rec | **0.9778 / 1.0000 / 0.9545** | `scripts/evaluate_hospital_matcher_extended.py` | `data/evaluation/hospital_matcher_results.json` | `7fc8e41` | 42 | Held-out test pairs ($N=45$) |
| **Table VIII: Matcher** | Test Set Ablation Prec / Spec | **0.7778 / 0.7391** | `scripts/evaluate_hospital_matcher_extended.py` | `data/evaluation/hospital_matcher_results.json` | `7fc8e41` | 42 | Test pairs, strict location disabled |
| **Table VIII: Matcher** | Full Set Acc / Prec / Rec | **0.9867 / 1.0000 / 0.9737** | `scripts/evaluate_hospital_matcher_extended.py` | `data/evaluation/hospital_matcher_results.json` | `7fc8e41` | 42 | All pairs ($N=75$) |
| **Hospital Network Part 1** | Real Sample Size / Linked | **10 records / 6 linked** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | `health_insurance.db` (`insurer_hospital_records`) |
| **Hospital Network Part 1** | Linked Recall | **100.0% (6 / 6)** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | National directory linked rows |
| **Hospital Network Part 1** | Bagalkot Scope Isolation | **100.0% (20 / 20 UNVERIFIED)** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | Bagalkot facilities ($N=20$) |
| **Hospital Network Part 1** | Distant States Isolation | **100.0% (50 / 50 UNVERIFIED)** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | Andaman, Assam, Bihar ($N=50$) |
| **Hospital Network Part 2** | Synthetic Stress Sample Size | **125 synthetic records** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | `synthetic_hospital_stress_sample.json` |
| **Hospital Network Part 2** | Target Recall / Isolation | **100% / 100%** | `scripts/evaluate_hospital_network.py` | `data/evaluation/hospital_network_results.json` | `7fc8e41` | 42 | Labeled synthetic stress test |
| **Table IX: Implemented** | BM25 Latency / Deps | **1.25 ms / Zero-Deps** | `scripts/evaluate_rag_frameworks_comparison.py` | `data/evaluation/rag_frameworks_comparison.json` | `7fc8e41` | 42 | SQLite FTS5 in-memory query |
| **Table IX: Implemented** | Hybrid Hash Latency / Deps | **2.07 ms / Zero-Deps** | `scripts/evaluate_rag_frameworks_comparison.py` | `data/evaluation/rag_frameworks_comparison.json` | `7fc8e41` | 42 | FTS5 + NumPy feature hash |
| **Table IX: Implemented** | Hybrid MiniLM Latency / Deps | **66.58 ms / PyTorch** | `scripts/evaluate_rag_frameworks_comparison.py` | `data/evaluation/rag_frameworks_comparison.json` | `7fc8e41` | 42 | FTS5 + SentenceTransformer |

---

## 3. Quarantined Legacy Simulated Artifacts

All previously generated simulated, hardcoded, or unverified evaluation artifacts were quarantined into `data/evaluation/quarantine/` and deleted from production evaluation pathways:

1. `quarantine/embeddings_collision_results.json`: Contained simulated collision estimates; replaced with real measurements across 3,155 vocabulary tokens, 12,786 bigrams, and 20,593 4-grams in `data/evaluation/embeddings_collision_results.json`.
2. `quarantine/evidence_gate_results.json`: Contained simulated gate distributions; replaced with passage-level evaluation against gold chunks in `data/evaluation/evidence_gate_results.json`.
3. `quarantine/generation_quality_results.json`: Contained simulated unconstrained LLM responses; replaced with real extractive synthesis lexical proxies and `[NOT RUN - Local LLM offline]` in `data/evaluation/generation_quality_results.json`.
4. `quarantine/hospital_matcher_results.json`: Contained un-split evaluation without ablation; replaced with dev/test split and strict location ablation in `data/evaluation/hospital_matcher_results.json`.
5. `quarantine/hospital_network_results.json`: Previously described synthetic 125 records as real Star Health data; replaced with honest separation of the 10-record real sample and synthetic stress test in `data/evaluation/hospital_network_results.json`.
6. `quarantine/ir_metrics_results.json`: Contained fake `hash()` semantic dense model; replaced with real SentenceTransformer `all-MiniLM-L6-v2` in `data/evaluation/ir_metrics_results.json`.
7. `quarantine/rag_frameworks_comparison.json`: Contained hardcoded comparative rows for CRAG and LangChain; replaced with empirical metrics from implemented systems and qualitative literature analysis in `data/evaluation/rag_frameworks_comparison.json`.

---

## 4. Software Verification & Unit Tests

All pipeline fixes, backward-compatibility facades, and scope filters pass the test suite:
- **Pytest**: `pytest backend/tests` $\to$ **60 passed in 14.56s**.
- **Location Check Test**: `backend/tests/test_phase1_fixes.py` validates that `strict_location_check=True` blocks false cross-jurisdiction linkages.
- **Frontend Build**: `npm --prefix frontend run build` validates TypeScript and Vite production compilation.
