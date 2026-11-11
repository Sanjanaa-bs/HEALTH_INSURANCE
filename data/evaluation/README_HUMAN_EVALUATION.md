# Evaluation Sheets & Instructions

This directory contains the experimental evaluation artifacts for Paper ID [907] (ICICF-2027).

## Sheets for Human Review

1. **`generation_quality_human_rating_sheet.csv`**
   - Contains all 65 benchmark questions, ground truth summaries, system extracted answers, and retrieved citations.
   - For **two independent human raters** to score factual correctness, citation accuracy, completeness, faithfulness, and hallucination.
   - See detailed rubric in [`../../docs/HUMAN_EVALUATION_PROTOCOL.md`](../../docs/HUMAN_EVALUATION_PROTOCOL.md).

2. **`benchmark_answers_human_review_sheet.csv`**
   - Contains all 65 benchmark questions, expected document references, page numbers, and ground-truth clause summaries.
   - For an **independent human auditor** (not the system authors) to cross-check each answer against the official policy PDFs.

## Evaluation Scripts (in `../../scripts/`)
- `evaluate_ir_metrics.py`: Standard IR metrics (P@K, R@K, MRR, nDCG@K).
- `evaluate_generation_quality.py`: Automated generation quality metrics.
- `evaluate_embeddings_and_collisions.py`: Feature hashing collision rate analysis ($d=64$ to $4096$).
- `evaluate_evidence_gate.py`: Precision, Recall, Specificity, and Distractor Rejection.
- `evaluate_hospital_matcher_extended.py`: Entity resolution stress test on 75 challenging pairs.
- `evaluate_hospital_network.py`: Multi-city network verification (125 records vs 29,974 directory).
- `evaluate_multi_policy_corpus.py`: Multi-policy corpus scaling (441 chunks, 8 documents, 4 insurers).
- `evaluate_rag_frameworks_comparison.py`: Comparative analysis against existing RAG frameworks.
- `export_human_evaluation_sheets.py`: Generates the above CSV sheets from live database queries.

