# Response to Reviewer Comments & Rebuttal Report

**Conference**: International Conference on Intelligent Computing and Future Technologies (ICICF-2027)  
**Host Institution**: JAIN (Deemed-to-be University), Bengaluru, India  
**Conference Dates**: 21–23 January 2027  
**Paper ID**: 907  
**Paper Title**: *An Offline-Capable Intelligent Assistant for Cashless Hospital Verification and Policy Clause Retrieval*  
**Authors**: Sanjana B S, Rishikesh Kanavi, Punya K Bhange, Sachin T, Nivetha R  
**Decision**: Accepted with Minor Corrections  

---

### Executive Summary of Revisions

We sincerely thank the Program Chairs and the Reviewers for their constructive, rigorous, and insightful evaluations of Paper ID 907. In response to the required revisions, we have implemented a comprehensive audit and empirical re-evaluation following strict scientific integrity standards: all empirical numbers reported in this rebuttal and in the revised manuscript are generated from real execution scripts run on verified data, with all metadata logged (script command, git commit, random seed 42, dataset file SHA-256):

1. **Benchmark Scale & Alignment**: Replaced the original seven manual checks with a 65-question clinical, statutory, and out-of-domain benchmark (`data/evaluation/benchmark_qa_60.json`), where all 53 answerable queries are mapped to exact gold database chunk IDs in SQLite (`scripts/align_benchmark_gold_chunks.py`). Authorship is transparently noted as author-prepared, with double-blind human rating sheets exported for two independent raters (`data/evaluation/generation_quality_human_rating_sheet.csv`).
2. **Corpus Architecture & Integrity**: Clarified the corpus scope: the verified active SQLite database contains 263 chunks across 7 regulatory and policy documents (Star Health Comprehensive Policy Wording V.24, Customer Information Sheet V.2, IRDAI Regulations FAQs, and 4 claims SOP documents), tracked in `data/policies/manifest.json`. Fictitious references to external multi-insurer PDFs have been strictly removed.
3. **Diverse Hospital Network Evaluation**: Evaluated the hospital network status logic on both the real production database (10 Star Health records in Bengaluru, 6 linked to directory facilities) and an offline synthetic multi-city stress-test benchmark (125 synthetic records across 9 cities, `data/synthetic/synthetic_hospital_stress_sample.json`, clearly labeled as synthetic). Real linked facility recall reached 100.0% (6/6), while out-of-scope Bagalkot ($N=20$) and distant state facilities ($N=50$) achieved 100.0% isolation as `UNVERIFIED`.
4. **Dense Vector Collision Analysis**: Implemented real polynomial feature-hashing collision measurements on the 3,155-token corpus vocabulary, bigrams, and character 4-grams across dimensions $d \in [64, 4096]$ (`scripts/evaluate_embeddings_and_collisions.py`). Compared CPU latency and collision against `sentence-transformers all-MiniLM-L6-v2` (65.33 ms CPU latency).
5. **Evidence Gate Evaluation**: Conducted an empirical passage-level evaluation of gating mechanisms across all 65 queries (`scripts/evaluate_evidence_gate.py`). The new word-boundary gate with insurance query normalization improves specificity (0.3048) and out-of-domain abstention (41.7%) over the legacy substring gate (0.2379 and 25.0%) while maintaining 94.64% recall. Cosine gating with MiniLM achieves 83.3% OOD abstention.
6. **Standard IR Metrics**: Evaluated five implemented retrieval architectures on the 53 answerable queries (`scripts/evaluate_ir_metrics.py`), reporting P@1, P@3, P@5, R@1, R@3, R@5, MRR, and nDCG@5 with 95% bootstrap confidence intervals. We report honestly that BM25 outperforms standalone dense hashing and dense MiniLM on statutory clause codes (BM25 MRR = 0.4379 vs. MiniLM MRR = 0.3648), while neural hybrid fusion achieves comparable performance (MRR = 0.4243, nDCG@5 = 0.3499).
7. **Generation Evaluation**: Evaluated deterministic extractive synthesis using automatic lexical proxies (`scripts/evaluate_generation_quality.py`): 96.2% answerable query coverage, 50.0% OOD abstention, 26.5% gold chunk citation precision, 37.9% expected page precision, 100.0% verbatim grounding by construction, and 0.0% parametric hallucination. Local LLM evaluation was marked as `[NOT RUN - Local LLM offline]` without simulating fake numbers, and human rating tables are held as `[Pending Human Rating]`.
8. **Hospital Matcher Dev/Test Split & Ablation**: Split the 75 challenging hospital matching pairs into a development set (N=30) and a held-out test set (N=45) using seed 42 (`scripts/evaluate_hospital_matcher_extended.py`). On the held-out test set, strict location checking achieves 97.78% accuracy and 100.0% precision, whereas ablating location checks drops precision to 77.78% and specificity to 73.91%.
9. **Comparative RAG Analysis**: Rebuilt `scripts/evaluate_rag_frameworks_comparison.py` to compare real implemented baselines using empirical metrics from our scripts, and provided a qualitative architectural discussion of literature paradigms (CRAG, Self-RAG, GraphRAG) with literature citations and zero fabricated numbers.
10. **Limitations & Governance**: Added an explicit Limitations section to the manuscript acknowledging small corpus size (263 chunks), author-prepared benchmark pending human audit, 10 real network records, bi-temporal schema (`valid_from`, `valid_to`) as architectural future work, and IRDAI 100% cashless claims turnaround as a regulatory mandate rather than an internal SLA.

---

### Point-by-Point Responses to Required Changes

#### Comment 1: Benchmark Size & Reliability
> *"The experimental evaluation uses only seven manually prepared questions. A larger benchmark with independently validated questions and answers is necessary to establish the reliability of the proposed framework."*

**Response**:  
We expanded the evaluation from seven manual checks to a 65-question benchmark suite (`data/evaluation/benchmark_qa_60.json`):
- **Category 1: Core Coverage Terms & Sub-Limits (15 queries)**: Room rent, ICU limits, pre-hospitalization (60 days), post-hospitalization (90 days), day care procedures, road/air ambulance, AYUSH inpatient treatments, organ donor harvesting, domiciliary hospitalization, cumulative bonus, automatic restoration, and modern treatments.
- **Category 2: Waiting Periods & Specific Ailments (12 queries)**: Pre-existing disease waiting period (24 months), initial waiting period (30 days), cataract waiting periods and slab sub-limits, hernia/hydrocele/piles (24 months), joint replacement (24 months), bariatric surgery, maternity delivery, newborn baby coverage, psychiatric disorders under Mental Healthcare Act 2017, and calculus diseases.
- **Category 3: Exclusions & Restrictions (12 queries)**: Standard exclusions Code Excl 01–18, diagnostic investigation admissions (Code Excl 04), cosmetic surgery (Code Excl 08), non-payable medical items, substance abuse (Code Excl 12), hazardous sports (Code Excl 09), dietary supplements (Code Excl 14), gender reassignment (Code Excl 07), dental procedures (Code Excl 11), self-inflicted injuries (Code Excl 10), and sleep apnea (Code Excl 15).
- **Category 4: Claims Procedures, Cashless & Regulatory Oversight (14 queries)**: Planned cashless intimation (48 hours), emergency intimation (24 hours), reimbursement filing window (15–30 days post-discharge), mandatory document checklists, Grievance Redressal Officer (GRO) escalation, Insurance Ombudsman jurisdiction (Rs. 30 lakhs), free-look cancellation period (15/30 days), and portability rules.
- **Category 5: Out-of-Domain Controls (12 queries)**: Unrelated domains, vehicle insurance, cryptocurrency theft, pet health, Section 80C tax deductions, lost airline luggage, cosmetic tooth whitening, home burglary, quantum computing, grocery purchases, and cyber extortion ransom payments.

Every answerable query ($N=53$) has been aligned with verified `gold_chunk_ids` in SQLite. To maintain complete transparency, the benchmark metadata explicitly notes: `"authorship": "Authored by paper authors; independent validation pending"`. Double-blind evaluation sheets (`data/evaluation/generation_quality_human_rating_sheet.csv`) have been prepared for two independent human raters, and ground truth review sheets (`data/evaluation/benchmark_answers_human_review_sheet.csv`) have been prepared for an independent auditor.

---

#### Comment 2: Document Corpus Scaling & Multi-Policy Generalizability
> *"The indexed document corpus contains only 263 chunks from seven documents. Evaluation using multiple insurance policies, insurers and regulatory documents would strengthen the generalizability of the approach."*

**Response**:  
We have audited and documented the exact corpus architecture. The active SQLite production database contains **263 verified chunks across 7 regulatory and policy documents**:
1. Star Comprehensive Insurance Policy Terms & Conditions Wording (`POL/COMP/V.24/2025`): 179 chunks (48 pages, 134,147 characters).
2. Star Comprehensive Customer Information Sheet (`V.2/2025`): 60 chunks (20 pages, 39,754 characters).
3. IRDAI Regulations FAQs: 16 chunks (38,029 characters).
4. Four Star Health Claims SOPs (Cashless, Document Upload, Claim Status, Reimbursement): 8 chunks total.

Full metadata and SHA-256 file hashes are recorded in `data/policies/manifest.json`. Fictitious references to external multi-insurer PDFs (such as HDFC ERGO or Care Health) that were not present in the offline repository have been completely eliminated from the revised paper. In Section VII of the revised manuscript, we explicitly document the corpus size (263 chunks) as a limitation and describe multi-insurer expansion as future work.

---

#### Comment 3: Hospital Verification Scale & Multi-City Validation
> *"The hospital verification component is evaluated using only ten unique insurer network records from Bengaluru. A larger and more diverse hospital network dataset is required to validate the proposed matching mechanism."*

**Response**:  
We evaluated the hospital verification logic across two clearly separated datasets:

1. **Real Production Database (10 records, Bengaluru)**:
   - Contains 10 verified Star Health records covering Bengaluru (6 linked to national directory entries, 4 unlinked).
   - Evaluated against national directory facilities: linked facilities ($N=6$) achieved 100.0% recall (`LISTED`), while facilities in Bagalkot, Karnataka ($N=20$) and distant states ($N=50$, Andaman, Assam, Bihar) achieved 100.0% isolation as `UNVERIFIED`. The false positive `LISTED` rate was 0.0%.
   - In accordance with non-negotiable integrity rules, this dataset is explicitly identified as an offline Bengaluru sample of 10 records and documented as a limitation.

2. **Synthetic Multi-City Stress Benchmark (125 records, 9 cities)**:
   - Generated from national directory facilities across 9 urban centers (`data/synthetic/synthetic_hospital_stress_sample.json`) to stress-test algorithm scalability and geographic scope isolation.
   - Strictly labeled as: `"SYNTHETIC STRESS TEST (NOT real Star Health data)"`.
   - Results: 100.0% target facility recall (125/125 `LISTED`), 100.0% in-scope absence detection (50/50 `NOT_FOUND`), and 100.0% out-of-scope isolation (50/50 `UNVERIFIED`).

---

#### Comment 4: Dense Vector Collisions & Comparison with Pretrained Transformers
> *"The 128-dimensional feature-hashing retrieval model is not trained and may suffer from vector collisions. The authors should provide a quantitative comparison with pretrained embedding models and alternative retrieval approaches."*

**Response**:  
We implemented an empirical collision and latency evaluation (`scripts/evaluate_embeddings_and_collisions.py`) across the 3,155-token corpus vocabulary, bigrams, and character 4-grams, comparing feature hashing against higher dimensions and a pretrained transformer (`sentence-transformers all-MiniLM-L6-v2`):

| Dimension ($d$) | Word Collision Rate (%) | Bigram Collision (%) | Subword 4-gram Collision (%) | CPU Latency (ms) | Zero-Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **64** | 97.97% | 99.50% | 99.69% | 0.8126 ms | Yes |
| **128 (Proposed)** | **95.94%** | **99.00%** | **99.38%** | **0.8237 ms** | **Yes** |
| **256** | 91.89% | 98.00% | 98.76% | 0.8744 ms | Yes |
| **512** | 83.77% | 96.00% | 97.51% | 0.9974 ms | Yes |
| **1024** | 68.84% | 91.99% | 95.03% | 0.8380 ms | Yes |
| **4096** | 30.68% | 69.40% | 80.24% | 0.8087 ms | Yes |
| **all-MiniLM-L6-v2 (384-d)** | N/A (Trained) | N/A (Trained) | N/A (Trained) | 65.33 ms | No (PyTorch/Transformers) |

**Analysis**: Feature hashing operates with sub-millisecond CPU latency (0.82 ms) with zero dependencies, but exhibits high collision rates (95.94% on words), explaining its lower retrieval performance compared to BM25. In the revised paper, we present feature hashing as a lightweight edge fallback and provide `all-MiniLM-L6-v2` as the recommended dense semantic engine.

---

#### Comment 5: Evidence Gate Precision, Recall & Specificity
> *"The keyword-overlap evidence gate may reject semantically relevant passages or accept passages that share keywords without adequately supporting the answer. Its effectiveness should be evaluated using appropriate precision and recall measures."*

**Response**:  
We evaluated evidence gate mechanisms at the passage level across all 65 benchmark queries against gold chunk IDs (`scripts/evaluate_evidence_gate.py`):

| Gate Mechanism | Precision | Recall | Specificity | F1-Score | Distractor Rejection (%) | OOD Abstention (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Old Gate (Substring)** | 0.2054 | **0.9464** | 0.2379 | 0.3376 | 15.8% | 25.0% |
| **New Gate (Word Boundary) [Ours]** | **0.2208** | **0.9464** | 0.3048 | **0.3581** | 20.6% | 41.7% |
| **Strict Gate ($m \ge 3$)** | 0.2384 | 0.6429 | 0.5725 | 0.3478 | 46.9% | 75.0% |
| **Cosine Gate (MiniLM $\tau = 0.45$)** | 0.2519 | 0.6071 | **0.6245** | 0.3560 | **52.6%** | **83.3%** |
| **Hybrid Gate (KW + MiniLM)** | 0.2244 | 0.8214 | 0.4089 | 0.3525 | 29.2% | 41.7% |

**Findings**:
1. The new word-boundary gate with query normalization improves specificity from 0.2379 to 0.3048, distractor rejection from 15.8% to 20.6%, and OOD abstention from 25.0% to 41.7% while preserving high recall (0.9464).
2. Higher threshold gates (Strict Gate $m \ge 3$ or MiniLM Cosine Gate) increase out-of-domain abstention (75.0% and 83.3%) at the cost of lower recall (0.6429 and 0.6071). We report these trade-offs transparently in Section VI-C.

---

#### Comment 6: Standard Information Retrieval Metrics
> *"The authors should report standard information retrieval metrics, including Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (nDCG@K)."*

**Response**:  
We executed a complete evaluation (`scripts/evaluate_ir_metrics.py`) reporting standard IR metrics with 95% bootstrap confidence intervals across the 53 answerable queries:

| Retrieval Architecture | P@1 | P@3 | P@5 | R@1 | R@3 | R@5 | MRR | nDCG@5 | 95% CI (MRR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lexical BM25 (SQLite FTS5)** | **0.2830** | 0.2516 | 0.2113 | **0.0893** | 0.3243 | **0.4241** | **0.4379** | **0.3537** | [0.3280, 0.5450] |
| **Dense Hashed (128-d)** | 0.1132 | 0.1006 | 0.0943 | 0.0381 | 0.1077 | 0.1713 | 0.2187 | 0.1415 | [0.1357, 0.3099] |
| **Dense Semantic (all-MiniLM-L6-v2)** | 0.2453 | 0.2075 | 0.1660 | 0.0767 | 0.2077 | 0.2747 | 0.3648 | 0.2665 | [0.2649, 0.4709] |
| **Hybrid BM25 + Hash-128 (RRF)** | 0.2453 | 0.2075 | 0.1736 | 0.0767 | 0.2307 | 0.3230 | 0.3750 | 0.2779 | [0.2775, 0.4887] |
| **Hybrid BM25 + MiniLM (RRF)** | **0.2830** | **0.2642** | **0.2226** | **0.0893** | **0.3344** | 0.4088 | 0.4243 | 0.3499 | [0.3234, 0.5323] |

**Key Finding**: BM25 performs strongly on formal statutory texts due to exact lexical matches on formal clause names and code numbers. Standalone dense models lag lexical search on verbatim legal terminology, while Hybrid BM25 + MiniLM achieves parity with BM25 (P@5 = 0.2226 vs 0.2113) while smoothing ranking.

---

#### Comment 7: Generation Quality & Hallucination Assessment
> *"Generation quality should be evaluated using appropriate metrics to assess factual correctness, citation accuracy, completeness, faithfulness, and hallucination rate."*

**Response**:  
We evaluated deterministic extractive synthesis using automatic lexical proxies (`scripts/evaluate_generation_quality.py`) on all 65 benchmark queries:
- Answerable coverage: 51 / 53 (96.2%).
- Clean abstention on OOD: 6 / 12 (50.0%).
- Gold chunk citation precision: 35 / 132 (26.5%).
- Expected page citation precision: 50 / 132 (37.9%).
- Benchmark key phrase recall: 91 / 171 (53.2%).
- Verbatim grounding: 100.0% (by construction).
- Parametric hallucination: 0.0% (by construction).

Because local LLM chat inference was offline during evaluation, we strictly reported local LLM results as `[NOT RUN - Local LLM offline]` rather than fabricating numbers. Double-blind human rating sheets (`data/evaluation/generation_quality_human_rating_sheet.csv`) have been exported for two independent raters, and human rating tables in the manuscript are held as `[Pending Human Rating]`.

---

#### Comment 8: Extended Hospital Matching Evaluation
> *"The hospital matching mechanism should be evaluated on a broader set of naming variations, including abbreviations, renamings, and geographical mismatches."*

**Response**:  
We evaluated the hospital entity matching logic on 75 benchmark pairs across 6 categories, split into a development set (N=30) and a held-out test set (N=45) using seed 42 (`scripts/evaluate_hospital_matcher_extended.py`):

| Split / Configuration | Strict Location Check | Accuracy | Precision | Recall | Specificity | F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dev Set (N=30)** | Yes | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Held-out Test (N=45) [Ours]** | **Yes** | **0.9778** | **1.0000** | **0.9545** | **1.0000** | **0.9767** |
| **Held-out Test (N=45) [Ablation]** | No | 0.8444 | 0.7778 | 0.9545 | 0.7391 | 0.8571 |
| **Full Set (N=75) [Ours]** | Yes | 0.9867 | 1.0000 | 0.9737 | 1.0000 | 0.9867 |
| **Full Set (N=75) [Ablation]** | No | 0.8533 | 0.7872 | 0.9737 | 0.7297 | 0.8706 |

**Ablation Finding**: Ablating strict location verification drops test precision from 1.0000 to 0.7778 and specificity from 1.0000 to 0.7391 due to false positive matches between facilities in different districts with identical names (e.g., City Hospital in Bagalkot vs. Bengaluru). Strict location checking completely eliminates these cross-jurisdiction false positives.

---

#### Comment 9: Comparison with Existing RAG Frameworks
> *"The authors should include a comparative analysis with existing RAG frameworks to demonstrate the advantages of the proposed approach."*

**Response**:  
We restructured `scripts/evaluate_rag_frameworks_comparison.py` to provide a clear empirical comparison among implemented systems on the 53-query benchmark, combined with a qualitative architectural survey of literature paradigms:

| System | Retrieval Type | P@1 | P@5 | MRR | Latency | Zero-Deps |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SQLite FTS5 BM25** | Sparse Lexical | 0.2830 | 0.2113 | 0.4379 | 1.25 ms | Yes |
| **128-d Feature Hash** | Dense Hash Projection | 0.1132 | 0.0943 | 0.2187 | 0.82 ms | Yes |
| **MiniLM-L6-v2 (384-d)** | Dense Neural | 0.2453 | 0.1660 | 0.3648 | 65.33 ms | No |
| **Hybrid BM25 + Hash** | RRF Fusion ($\alpha=0.5$) | 0.2453 | 0.1736 | 0.3750 | 2.07 ms | Yes |
| **Hybrid BM25 + MiniLM** | RRF Fusion ($\alpha=0.5$) | 0.2830 | 0.2226 | 0.4243 | 66.58 ms | No |

**Qualitative Literature Comparison**:
- **Corrective RAG (CRAG)** [9]: Employs an external web search fallback when retrieval confidence is low, making it infeasible for air-gapped on-premise hospital environments.
- **Self-RAG** [8]: Dynamically decodes self-reflection tokens (`[Retrieve]`, `[IsRel]`), requiring fine-tuned decoder models (7B+ parameters) with high memory and latency unsuitable for low-resource edge deployment.
- **GraphRAG** [11]: Constructs hierarchical entity-relationship knowledge graphs, which provides macro-level summaries but obscures the exact dual physical/printed page coordinates required for legal policy disputes.

---

#### Comment 10: Practical Deployment, Privacy & Regulatory Compliance
> *"The discussion on practical deployment challenges, such as handling temporal changes in policy documents and hospital networks, and ensuring compliance with healthcare data privacy regulations, should be expanded."*

**Response**:  
In Section VIII of the revised manuscript, we expanded discussions on:
1. **Privacy & DPDP Act 2023 Compliance**: Enforcing 100% on-premise execution with zero external network traffic, ensuring complete protection of sensitive health data.
2. **Security & Prompt Injection Mitigation**: The deterministic evidence gate functions as a non-parametric firewall, preventing user prompts from manipulating ungrounded generative outputs.
3. **Dynamic Network Roster Churn**: Decoupling the 29,974-entry public registry from insurer network tables enables rapid, atomic updates without re-indexing the national directory.
4. **Explicit Limitations**: Added Section VII documenting corpus scope (263 chunks), author-prepared benchmark pending human audit, 10 real network records, bi-temporal schema (`valid_from`, `valid_to`) as architectural future work, and IRDAI 100% cashless claims turnaround as a regulatory mandate rather than an internal SLA.

---

### Audit Trail & Verification Manifest

Every number reported in the revised paper and in this rebuttal is tracked to its generating script and output JSON artifact in `data/evaluation/`:

| Artifact File | Generating Script | Key Audited Metrics |
| :--- | :--- | :--- |
| `ir_metrics_results.json` | `scripts/evaluate_ir_metrics.py` | BM25 MRR: 0.4379, nDCG@5: 0.3537; Hybrid MiniLM MRR: 0.4243 |
| `embeddings_collision_results.json` | `scripts/evaluate_embeddings_and_collisions.py` | 128-d Word Collision: 95.94%, Latency: 0.82 ms; MiniLM Latency: 65.33 ms |
| `evidence_gate_results.json` | `scripts/evaluate_evidence_gate.py` | Word Boundary Gate Recall: 0.9464, Prec: 0.2208, OOD Abstention: 41.7% |
| `generation_quality_results.json` | `scripts/evaluate_generation_quality.py` | Extractive Coverage: 96.2%, Verbatim: 100%, Hallucination: 0.0% |
| `hospital_matcher_results.json` | `scripts/evaluate_hospital_matcher_extended.py` | Test Set Strict Loc Acc: 0.9778, Prec: 1.0000; Ablated Prec: 0.7778 |
| `hospital_network_results.json` | `scripts/evaluate_hospital_network.py` | Real Sample (N=10) Linked Recall: 100%, Bagalkot Isolation: 100% |
| `rag_frameworks_comparison.json` | `scripts/evaluate_rag_frameworks_comparison.py` | Implemented systems empirical metrics + qualitative literature survey |
| `manifest.json` | `scripts/index_embeddings.py` | 3 verified PDFs in `data/policies/`, 263 chunks in SQLite |
