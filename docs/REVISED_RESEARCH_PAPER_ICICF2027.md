# An Offline-Capable Intelligent Assistant for Cashless Hospital Verification and Policy Clause Retrieval

**Authors**:  
- **Sanjana B S**, Department of CSE (AI & ML), Dayananda Sagar University, Bengaluru, India (`sanjanaabs@gmail.com`)  
- **Rishikesh Kanavi**, Department of CSE (AI & ML), Dayananda Sagar University, Bengaluru, India (`rishikeshkanavi04@gmail.com`)  
- **Punya K Bhange**, Department of CSE (AI & ML), Dayananda Sagar University, Bengaluru, India (`punyabhange30@gmail.com`)  
- **Sachin T**, Department of CSE (AI & ML), Dayananda Sagar University, Bengaluru, India (`sachinraj060405@gmail.com`)  
- **Nivetha R**, Department of CSE (AI & ML), Dayananda Sagar University, Bengaluru, India (`nivetha.r-aiml@dsu.edu.in`)  

**Conference**: International Conference on Intelligent Computing and Future Technologies (ICICF-2027)  
**Venue**: JAIN (Deemed-to-be University), Bengaluru, India  
**Paper ID**: 907  

---

## Abstract

Most Indian policyholders face immense difficulty deciphering dense, clause-filled health insurance policies, verifying whether a hospital belongs to an insurer's cashless network, and navigating complex claim procedures. General-purpose Large Language Models (LLMs) frequently hallucinate non-existent benefits, misquote waiting periods, or fabricate page citations, introducing legal and financial risks for patients during emergency hospitalizations. 

In this paper, the authors present a locally deployable, privacy-preserving assistant combining a hybrid retrieval pipeline with a strict deterministic abstention policy and spatial entity resolution. Regulatory documents, customer information sheets, claims guidance, and standardized policies are segmented into 263 chunks with dual-page coordinate binding (physical and printed page numbers) and SHA-256 cryptographic provenance. Passages are indexed via SQLite FTS5 (BM25) and a lightweight 128-dimensional feature-hashing dense channel fused through Reciprocal Rank Fusion (RRF, $\alpha = 0.5, k = 60$), filtered by a keyword-overlap evidence gate ($m \ge 2$), and synthesized into grounded answers with verified citations. When evidence is insufficient, the system enforces clean abstention. A conservative entity resolution algorithm connects 29,974 facilities from the national registry with insurer network records, enforcing a tri-state network status (`LISTED`, `NOT_FOUND`, `UNVERIFIED`). 

In extensive empirical benchmarks across 65 clinical and statutory queries (53 answerable, 12 out-of-domain), the BM25 retrieval engine achieves an **MRR of 0.4379**, **nDCG@5 of 0.3537**, and **P@1 of 0.2830**, while a dense neural model (all-MiniLM-L6-v2) achieves **MRR of 0.3648** and **nDCG@5 of 0.2665**, and neural hybrid fusion achieves **MRR of 0.4243** and **nDCG@5 of 0.3499**. The deterministic extractive synthesis mode eliminates parametric hallucinations by construction (100% verbatim passage grounding). The hospital matching mechanism achieves **97.78% accuracy** and **100.0% precision** on a held-out test set (N=45) under strict location checking, eliminating false positive cross-jurisdiction linkages. The entire architecture runs 100% on-premise without GPU dependencies, preserving full compliance with India's Digital Personal Data Protection Act 2023 with an average pure-CPU query retrieval latency of ~2.07 ms.

**Index Terms**—Abstention, BM25, cashless hospital verification, evidence-grounded question answering, health insurance, hybrid information retrieval, hospital network matching, policy clause retrieval, reciprocal rank fusion, offline deployment, DPDP Act 2023.

---

## I. Introduction

Purchasing health insurance is just the beginning; using it during a medical crisis is a daunting challenge. When a policyholder is admitted to a hospital, three critical questions immediately arise:
1. **Clause Restrictions**: Are there specific waiting periods, room-rent sub-limits, or disease-specific copayments that restrict coverage for this procedure?
2. **Network Admissibility**: Does the selected hospital accept the insurer's cashless facility, or must the patient pay out-of-pocket and seek reimbursement?
3. **Procedural Deadlines**: What documents, intimations, and statutory timelines (e.g., 48 hours for planned, 24 hours for emergency admission) are required to avoid claim repudiation?

The answers to these questions are fragmented across disparate sources: lengthy policy wordings (40–60 dense pages), a Customer Information Sheet (CIS), dynamic hospital web portals, and procedural guidance pages. Under stress, policyholders cannot reconcile these documents.

General-purpose Large Language Models (LLMs) appear attractive, but ungrounded generative models present severe failure modes in the legal and healthcare domains:
- **Hallucination of Coverage**: Fabricating coverage terms (e.g., asserting that cosmetic surgery or non-admitted maternity is payable).
- **Page Citation Dissociation**: Inability to link assertions to human-verifiable physical and printed page numbers of the underlying PDF contract.
- **Over-Answering Out-of-Domain Queries**: Failing to recognize absent evidence, violating the fundamental legal insurance principle that *absence of a match does not prove exclusion or coverage*.
- **Facility Conflation**: Confusing public government-registered healthcare directories with private insurer-negotiated cashless networks.

To address these vulnerabilities, this paper proposes an offline-capable, evidence-grounded architecture with four main contributions:
1. **Dual-Tier Hybrid Retrieval Pipeline**: Unifying BM25 lexical ranking and an unsupervised 128-dimensional dense feature-hashing channel via Reciprocal Rank Fusion (RRF), running entirely in CPU memory without external vector databases or PyTorch dependencies, with an optional neural transformer upgrade.
2. **Dual-Coordinate Provenance & Micro-Chunking**: A heading-aware sliding-window chunking algorithm capturing hierarchical legal headings, SHA-256 cryptographic digests, and simultaneous physical and printed page coordinates.
3. **Deterministic Evidence Gate**: A non-parametric lexical gate enforcing strict abstention on unanswerable and adversarial queries, preventing parametric hallucination.
4. **Conservative Spatial Entity Resolution**: A normalizer and location-compatibility validator mapping 29,974 national healthcare facilities to insurer network records, outputting a tri-state status (`LISTED`, `NOT_FOUND`, `UNVERIFIED`) with mandatory pre-authorization disclaimers.

---

## II. Related Work

### A. RAG for Legal and Healthcare Question Answering
Retrieval-Augmented Generation (RAG) grounds language model generations in retrieved context passages rather than relying solely on parametric memory [1]. In insurance, InsuranceRAG [1] introduces a multi-module assistant, while InsQABench [2] benchmarks Chinese insurance question answering. Our focus is distinct: exact dual-page policy citations, enforced mathematical abstention, and hospital cashless verification under Indian regulatory jurisprudence (IRDAI). Medical RAG studies emphasize that retrieval quality dominates generation faithfulness [3]–[6].

### B. Adaptive, Self-Reflective, and Agentic RAG
Recent work investigates adaptive retrieval strategies [7], self-reflective critique (Self-RAG) [8], corrective retrieval (CRAG) [9], and agentic multi-hop planning [10]. While effective in cloud settings, these architectures demand heavy GPU resources and multi-pass inference (>1.5 s latency). In contrast, our platform targets low-resource edge deployment at hospital billing desks, achieving deterministic verification in under 7 ms.

### C. Hybrid Retrieval and Rank Fusion
Combining sparse inverted indices (BM25) with dense representations overcomes the vocabulary mismatch problem while retaining lexical precision for statutory clause codes (e.g., "Code Excl 04", "single private A/C room") [6]. Reciprocal Rank Fusion (RRF) [4] provides robust rank combination without requiring score calibration across heterogeneous retrieval channels.

### D. Evaluation, Hallucination, and Privacy
RAGAs [12] and ARES [13] establish standard metrics for context relevance, groundedness, and answer faithfulness. RAGTruth [14] and recent uncertainty studies [15] emphasize that verbalized model confidence is unreliable. Given sensitive Personal Health Information (PHI) [20], privacy regulations (such as India's DPDP Act 2023) mandate on-premise, zero-leakage architectures [18], [19].

---

## III. Problem Formulation

Let $\mathcal{C} = \{c_1, \dots, c_N\}$ be the indexed document corpus of $N$ text chunks ($N = 263$). Each chunk $c$ carries metadata:
$$m(c) = (\text{doc}, \text{page}_{\text{phys}}, \text{page}_{\text{print}}, \text{heading}, h)$$
where $h = \text{SHA256}(\text{text}(c))$ guarantees cryptographic provenance.

Given a user query $q$, the question-answering system returns:
$$R(q) \in \{\text{ANSWER}(\mathcal{E}, a), \text{ABSTAIN}\}$$
where $\mathcal{E} \subseteq \mathcal{C}$ contains at most $K = 5$ cited passages, and $a$ is the generated or extracted answer text. We enforce two invariant requirements:
1. **Groundedness**: Every factual assertion in $a$ must be entailed by at least one passage in $\mathcal{E}$, accompanied by human-verifiable dual-page labels.
2. **Abstention**: If $\mathcal{E} = \emptyset$, the system must emit an explicit abstention response and refuse to generate policy terms.

For hospital verification, let $x$ denote a facility entry from the National Hospital Directory $\mathcal{D}$, and $\mathcal{I}$ denote the insurer cashless network records. The system computes a tri-state network status:
$$\sigma(x, \mathcal{I}) \in \{\text{LISTED}, \text{NOT\_FOUND}, \text{UNVERIFIED}\}$$

TABLE I: NOTATION
| Symbol | Meaning | Value / Definition |
| :--- | :--- | :--- |
| $\mathcal{C}, N$ | Chunk set and its total size | $N = 263$ active chunks across 7 regulatory/policy documents |
| $d$ | Dense vector feature dimension | $d = 128$ (polynomial feature hash) / $d = 384$ (MiniLM) |
| $K$ | Maximum cited passages | $K = 5$ |
| $r_b(c), r_v(c)$ | Rank of chunk $c$ in BM25 / vector channel | 1-indexed ranks |
| $\alpha$ | BM25 fusion weighting coefficient | $\alpha = 0.5$ |
| $k$ | RRF smoothing constant | $k = 60.0$ |
| $S(c)$ | Fused Reciprocal Rank Fusion score | Eq. (2) |
| $W(q)$ | Stopword-filtered meaningful query keywords | Eq. (3) |
| $m$ | Required keyword overlap threshold | $m \ge 2$ if $\|W(q)\| \ge 3$, else 1 |
| $\sigma(x, \mathcal{I})$ | Tri-state network verification status | Eq. (4) |

---

## IV. Datasets & Corpus Architecture

The platform operates across two foundational corpora: (i) Structured Healthcare Facility Registries, and (ii) Contractual & Regulatory Knowledge Bases.

### A. National Hospital Directory
Exported from the National Health Authority (NHA) public portal, containing 30,273 raw records. Following de-duplication and filtering of empty records, **29,974 valid healthcare facilities** across all 36 States and Union Territories are loaded into SQLite. Attributes include facility name, state, district, subdistrict, pincode, hospital category (public/private), care type, bed count, and contact details.

### B. Insurer Network Dataset & Geographic Scope
The verified insurer dataset in the production SQLite database contains **10 Star Health network records from Bengaluru, Karnataka**, of which 6 are linked via foreign keys to directory facilities and 4 are unlinked. Because this sample is geographically restricted to Bengaluru, queries for facilities outside Bengaluru (such as Bagalkot, Karnataka or South Andaman) are strictly classified as `UNVERIFIED` rather than `NOT_FOUND`. To evaluate algorithmic scaling and multi-city geographic isolation, an offline synthetic stress-test benchmark of 125 records across 9 urban centers (`data/synthetic/synthetic_hospital_stress_sample.json`) was generated from national directory entries.

### C. Active Document Corpus
The indexed text knowledge base contains **7 documents and 263 chunks** verified in SQLite:

TABLE II: ACTIVE DOCUMENT CORPUS
| Document Entity | Insurer / Authority | File Format | Chunks | Document Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Star Comprehensive Policy Terms** | Star Health | PDF (`data/policies/Policy_Star_Comprehensive_clean.pdf`) | 179 | Active Policy Wording (`POL/COMP/V.24/2025`) |
| **Customer Information Sheet (CIS)** | Star Health | PDF (`data/policies/CIS_Star_Comprehensive_Insurance_Policy_V_2_69c15a9ee1.pdf`) | 60 | Mandated Summary Table (`V.2/2025`) |
| **IRDAI Regulations FAQ** | IRDAI Regulator | MHTML (`data/claim_guidance/irdai_health_insurance_faqs.mhtml`) | 16 | Statutory Guidelines & Ombudsman Norms |
| **Cashless Claim SOP** | Star Health | MHTML (`data/claim_guidance/star_cashless_claims.mhtml`) | 2 | Online Cashless Pre-Auth Procedure |
| **Claim Document Upload SOP** | Star Health | MHTML (`data/claim_guidance/star_claim_document_upload.mhtml`) | 2 | Portal Document Submission SOP |
| **Claim Status SOP** | Star Health | MHTML (`data/claim_guidance/star_claim_status.mhtml`) | 2 | Online Claim Tracking SOP |
| **Reimbursement SOP** | Star Health | MHTML (`data/claim_guidance/star_reimbursement_claims.mhtml`) | 2 | Reimbursement Filing Guidance |
| **Total Active Corpus** | **Star Health & IRDAI** | **PDF / MHTML** | **263** | **Active Statutory Corpus** |

*Note*: Full file metadata and cryptographic hashes are tracked in `data/policies/manifest.json`.

---

## V. System Architecture

The platform comprises a three-layer decoupled architecture: a React 18 / TypeScript frontend, a FastAPI asynchronous backend, and a data layer comprising SQLite (with FTS5) and an atomic flat-file vector index.

### A. Heading-Aware Sliding-Window Chunking
PDFs are parsed with `pypdf` (with `PyMuPDF` fallback). Heading detection enforces:
$$\text{Heading} = \text{Uppercase} \lor \text{Matches}(\wedge(\text{section}|\text{clause}|\text{part}|\text{table}|\text{item}|\text{coverage}|\text{benefit}|\text{exclusion}|\text{condition})\backslash b) \lor \text{EndsWith}(":")$$
Chunks accumulate sentences until reaching **800 characters** ($\sim 160$ words). Upon boundary completion, a dynamic 1-line carryover is injected into the subsequent chunk to preserve antecedent contractual conditions. Dual-page mapping dynamically resolves total extracted pages from document metadata, stamped with SHA-256 digests.

### B. Lexical Retrieval Channel
Chunks are indexed in SQLite FTS5 using the `porter unicode61` tokenizer. Queries are lower-cased, expanded for common insurance terms ("before hospitalization" $\to$ "prehospitalization"), and filtered of domain stopwords. Strict `AND` matching is attempted first, falling back to `OR` matching with native BM25 ranking.

### C. Dense Feature-Hashing Channel
The default dense encoder requires zero training parameters and zero external model weights. For text $t$, let $U$ be its word tokens ($\ge 2$ characters), $B$ its adjacent word bigrams, and $G$ its character 4-grams. The unnormalized vector $\tilde{v}(t) \in \mathbb{R}^d$ ($d = 128$) is:
$$\tilde{v}(t) = \sum_{u \in U} 1.5 \, \mathbf{e}_{\eta(u)} + \sum_{b \in B} 1.0 \, \mathbf{e}_{\eta(b)} + \sum_{g \in G} 0.4 \, \mathbf{e}_{\eta(g)} \tag{1}$$
where $\mathbf{e}_j$ is the $j$-th standard basis vector and $\eta(s) = \left( \sum_{i} \text{ord}(s_i) \cdot 31^{|s|-1-i} \bmod 2^{32} \right) \bmod d$. Normalization applies strict Euclidean L2 projection: $v(t) = \tilde{v}(t) / (\|\tilde{v}(t)\|_2 + 10^{-6})$.

### D. Reciprocal Rank Fusion (RRF)
Given zero-indexed ranks $r_b(c)$ and $r_v(c)$ from BM25 and vector search:
$$S(c) = \frac{\alpha}{k + r_b(c) + 1} + \frac{1 - \alpha}{k + r_v(c) + 1} \tag{2}$$
with $\alpha = 0.5$ and $k = 60.0$.

### E. Deterministic Evidence Gate
Let $W(q)$ be the stopword-filtered keywords of query $q$. A fused candidate passage $c$ is accepted only if:
$$\text{hits}(c, q) \ge m, \quad m = \begin{cases} 2, & |W(q)| \ge 3 \\ 1, & \text{otherwise} \end{cases} \tag{3}$$
where $\text{hits}(c, q) = |\{w \in W(q) : w \in \text{text}(c)\}|$ using whole-word boundary regex and insurance term normalization. If no candidate satisfies Eq. (3), the system emits `insufficient_evidence`, returns an explicit warning banner, and bypasses generation.

### F. Grounded Extractive Synthesis
When citations clear the evidence gate, passages are supplied to a deterministic extractive synthesis engine that extracts verbatim clauses from retrieved text. Every response appends human-verifiable citations with physical and printed page coordinates and statutory disclaimers.

### G. Conservative Hospital Network Entity Resolution
To prevent falsely declaring a facility as in-network:
1. **Normalization $\nu(\cdot)$**: Translates `&` to `and`, strips apostrophes, standardizes Unicode NFKD to ASCII, maps `hospitals` to `hospital`, and removes corporate legal suffixes (`pvt`, `ltd`, `llp`, `inc`).
2. **Spatial Compatibility $\text{loc}(x, r)$**: Validates state agreement, city/district equivalence, and 3-digit pincode prefixes.
3. **Tri-State Determination**:
$$\sigma(x, \mathcal{I}) = \begin{cases} 
\text{UNVERIFIED}, & \mathcal{I} = \emptyset \lor \neg \text{in\_scope}(x, \mathcal{I}) \\ 
\text{LISTED}, & \exists r \in \mathcal{I} : (\text{link}(x, r) \lor (\nu(x) = \nu(r) \land \text{loc}(x, r))) \\ 
\text{NOT\_FOUND}, & \text{otherwise (in-scope unlisted)} 
\end{cases} \tag{4}$$

---

## VI. Experimental Results & Benchmarks

All reported metrics are generated directly from execution scripts logged with commit hashes, random seeds, and SHA-256 data hashes.

### A. Information Retrieval Benchmark Performance
Evaluated across 53 answerable statutory queries aligned with gold database chunk IDs:

TABLE IV: INFORMATION RETRIEVAL BENCHMARK PERFORMANCE (N=53 QUERIES)
| Retrieval Architecture | P@1 | P@3 | P@5 | R@1 | R@3 | R@5 | MRR | nDCG@5 | 95% CI (MRR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lexical BM25 (SQLite FTS5)** | **0.2830** | 0.2516 | 0.2113 | **0.0893** | 0.3243 | **0.4241** | **0.4379** | **0.3537** | [0.3280, 0.5450] |
| **Dense Hashed (128-d)** | 0.1132 | 0.1006 | 0.0943 | 0.0381 | 0.1077 | 0.1713 | 0.2187 | 0.1415 | [0.1357, 0.3099] |
| **Dense Semantic (all-MiniLM-L6-v2)** | 0.2453 | 0.2075 | 0.1660 | 0.0767 | 0.2077 | 0.2747 | 0.3648 | 0.2665 | [0.2649, 0.4709] |
| **Hybrid BM25 + Hash-128 (RRF)** | 0.2453 | 0.2075 | 0.1736 | 0.0767 | 0.2307 | 0.3230 | 0.3750 | 0.2779 | [0.2775, 0.4887] |
| **Hybrid BM25 + MiniLM (RRF)** | **0.2830** | **0.2642** | **0.2226** | **0.0893** | **0.3344** | 0.4088 | 0.4243 | 0.3499 | [0.3234, 0.5323] |

*Key Finding*: On formal insurance clauses, BM25 outperforms standalone dense hashing and dense MiniLM due to strict lexical matching on statutory terms ("Code Excl 04", "single private A/C room"). Hybrid BM25 + MiniLM achieves comparable performance (P@5 = 0.2226 vs 0.2113 for BM25) while smoothing ranking.

### B. Vector Collisions & Embedding Representation Comparison
Evaluating feature hashing across the 3,155-token corpus vocabulary:

TABLE V: DENSE FEATURE HASHING COLLISION & LATENCY ABLATION
| Dimension ($d$) | Word Collision Rate (%) | Bigram Collision (%) | Subword 4-gram Collision (%) | CPU Latency (ms) | Zero-Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **64** | 97.97% | 99.50% | 99.69% | 0.8126 ms | Yes |
| **128 (Ours)** | **95.94%** | **99.00%** | **99.38%** | **0.8237 ms** | **Yes** |
| **256** | 91.89% | 98.00% | 98.76% | 0.8744 ms | Yes |
| **512** | 83.77% | 96.00% | 97.51% | 0.9974 ms | Yes |
| **1024** | 68.84% | 91.99% | 95.03% | 0.8380 ms | Yes |
| **4096** | 30.68% | 69.40% | 80.24% | 0.8087 ms | Yes |
| **all-MiniLM-L6-v2 (384-d)** | N/A (Trained) | N/A (Trained) | N/A (Trained) | 65.33 ms | No (PyTorch/Transformers) |

Feature hashing operates with sub-millisecond CPU latency and zero external dependencies, though high collision rates explain its lower retrieval metrics compared to BM25.

### C. Evidence Gate Precision, Recall, and Specificity
Evaluating gate mechanisms across all 65 queries at the passage level:

TABLE VI: EVIDENCE GATE PASSAGE-LEVEL EVALUATION
| Evidence Gate Mechanism | Precision | Recall | Specificity | F1-Score | FAR | Distractor Rejection (%) | OOD Abstention (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Old Gate (Substring)** | 0.2054 | **0.9464** | 0.2379 | 0.3376 | 0.7621 | 15.8% | 25.0% |
| **New Gate (Word Boundary) [Ours]** | **0.2208** | **0.9464** | 0.3048 | **0.3581** | 0.6952 | 20.6% | 41.7% |
| **Strict Gate ($m \ge 3$)** | 0.2384 | 0.6429 | 0.5725 | 0.3478 | 0.4275 | 46.9% | 75.0% |
| **Cosine Gate (MiniLM $\tau = 0.45$)** | 0.2519 | 0.6071 | **0.6245** | 0.3560 | **0.3755** | **52.6%** | **83.3%** |
| **Hybrid Gate (KW + MiniLM)** | 0.2244 | 0.8214 | 0.4089 | 0.3525 | 0.5911 | 29.2% | 41.7% |

The new word-boundary gate with normalization improves specificity from 0.2379 to 0.3048 and OOD abstention from 25.0% to 41.7% while maintaining high recall (0.9464). Higher thresholds (Strict Gate or Cosine Gate) increase OOD abstention (75.0%–83.3%) at the cost of reduced recall (0.6071–0.6429).

### D. Generation Quality & Abstention Performance

TABLE VII: GENERATION EVALUATION (65 BENCHMARK QUERIES)
| Metric | Deterministic Extractive (Ours) | Grounded Local LLM | Unconstrained LLM |
| :--- | :--- | :--- | :--- |
| **Answerable Coverage** | 51 / 53 (96.2%) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **OOD Abstention Rate** | 6 / 12 (50.0%) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Gold Chunk Citation Precision** | 35 / 132 (26.5%) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Expected Page Citation Precision** | 50 / 132 (37.9%) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Benchmark Key Phrase Recall** | 91 / 171 (53.2%) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Verbatim Grounding** | 100.0% (by construction) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Parametric Hallucination** | 0.0% (by construction) | [NOT RUN - LLM offline] | [NOT RUN - LLM offline] |
| **Human Rating (1–5 Likert)** | [Pending Human Rating] | [Pending Human Rating] | [Pending Human Rating] |

*Note*: In accordance with scientific integrity guidelines, local LLM evaluation is reported as NOT RUN because Ollama chat inference was offline. Human evaluation sheets (`data/evaluation/generation_quality_human_rating_sheet.csv`) are prepared for double-blind human rating by two independent raters.

### E. Extended Hospital Normalization & Spatial Verification
Evaluated on 75 benchmark pairs split into a development set (N=30) and held-out test set (N=45):

TABLE VIII: HOSPITAL ENTITY MATCHING PERFORMANCE
| Split / Configuration | Strict Location Check | Accuracy | Precision | Recall | Specificity | F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dev Set (N=30)** | Yes | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Held-out Test (N=45) [Ours]** | **Yes** | **0.9778** | **1.0000** | **0.9545** | **1.0000** | **0.9767** |
| **Held-out Test (N=45) [Ablation]** | No | 0.8444 | 0.7778 | 0.9545 | 0.7391 | 0.8571 |
| **Full Set (N=75) [Ours]** | Yes | 0.9867 | 1.0000 | 0.9737 | 1.0000 | 0.9867 |
| **Full Set (N=75) [Ablation]** | No | 0.8533 | 0.7872 | 0.9737 | 0.7297 | 0.8706 |

Ablating strict location verification drops test precision from 1.0000 to 0.7778 and specificity from 1.0000 to 0.7391 due to false positive matches between facilities in different districts and states with identical names (e.g., City Hospital in Bagalkot vs. Bengaluru).

### F. Real Hospital Network Status & Synthetic Stress Benchmark
1. **Real Star Health Sample (10 records in SQLite, Bengaluru)**:
   - Linked Facilities ($N=6$): 6 / 6 correctly returned `LISTED` (100.0% recall).
   - Bagalkot Facilities ($N=20$, including Kerudi Hospital): 20 / 20 correctly returned `UNVERIFIED` (100.0% isolation).
   - Distant State Facilities ($N=50$, Andaman, Assam, Bihar): 50 / 50 correctly returned `UNVERIFIED` (100.0% isolation).
   - False positive `LISTED` rate: 0.0%.
2. **Synthetic Multi-City Stress Benchmark (125 synthetic records, 9 cities)**:
   - Evaluated as an offline algorithm stress test (`data/synthetic/synthetic_hospital_stress_sample.json`).
   - Target facilities ($N=125$): 125 / 125 returned `LISTED` (100.0%).
   - In-scope unlisted ($N=50$): 50 / 50 returned `NOT_FOUND` (100.0%).
   - Out-of-scope ($N=50$): 50 / 50 returned `UNVERIFIED` (100.0%).

### G. Comparative Framework Analysis

TABLE IX: COMPARATIVE ARCHITECTURAL BENCHMARK OF IMPLEMENTED SYSTEMS
| System | Retrieval Mechanism | P@1 | P@5 | R@5 | MRR | nDCG@5 | Latency (ms) | Zero-Deps |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SQLite FTS5 BM25** | Sparse Lexical | 0.2830 | 0.2113 | 0.4241 | 0.4379 | 0.3537 | 1.25 ms | Yes |
| **128-d Feature Hash** | Dense Hash Projection | 0.1132 | 0.0943 | 0.1713 | 0.2187 | 0.1415 | 0.82 ms | Yes |
| **MiniLM-L6-v2 (384-d)** | Dense Neural | 0.2453 | 0.1660 | 0.2747 | 0.3648 | 0.2665 | 65.33 ms | No |
| **Hybrid BM25 + Hash-128** | RRF Fusion ($\alpha=0.5$) | 0.2453 | 0.1736 | 0.3230 | 0.3750 | 0.2779 | 2.07 ms | Yes |
| **Hybrid BM25 + MiniLM** | RRF Fusion ($\alpha=0.5$) | 0.2830 | 0.2226 | 0.4088 | 0.4243 | 0.3499 | 66.58 ms | No |

**Qualitative Comparison with Advanced Paradigms**:
- **Corrective RAG (CRAG)** [9]: Evaluates retrieval confidence and falls back to live web search when confidence is low. While effective in cloud settings, reliance on external web search makes CRAG unviable for strictly offline or air-gapped deployments.
- **Self-RAG** [8]: Dynamically decodes self-reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`), requiring fine-tuned decoder models (7B+ parameters) with high GPU memory and decoding latency impractical on edge CPUs.
- **GraphRAG** [11]: Constructs hierarchical entity-relationship graphs. While offering macro-level query summarization, it obscures the exact dual physical/printed page coordinates required for legal policy disputes and incurs heavy indexing costs.

---

## VII. Limitations

1. **Corpus Scope**: The indexed document corpus currently contains 263 chunks across 7 regulatory and policy documents primarily centered on Star Health Comprehensive Insurance and IRDAI regulations. Generalization across other private and public insurers requires ingesting and indexing additional policy contracts.
2. **Benchmark Authorship & Validation Status**: The 65-question benchmark was prepared by the authors based on common policyholder queries and statutory terms. Double-blind human rating across two raters (`data/evaluation/generation_quality_human_rating_sheet.csv`) and independent audit of answer ground truths (`data/evaluation/benchmark_answers_human_review_sheet.csv`) are currently underway.
3. **Insurer Network Sample**: The production database contains 10 verified Star Health records covering Bengaluru (6 linked). The 125-record multi-city dataset evaluated in Section VI-F is a synthetic stress-test benchmark generated from the national directory to test multi-city algorithm scalability and is not a real insurer network dataset.
4. **Temporal Policy Tracking**: In the current implementation, versioning is tracked via static document version strings and SHA-256 digests. A full bi-temporal database schema (`valid_from`, `valid_to`) to track mid-term policy amendments and regulatory circular effective dates is proposed as architectural future work.
5. **Cashless Turnaround Standards**: The 100% cashless claims turnaround standards referenced in this work reflect statutory regulatory mandates established by the Insurance Regulatory and Development Authority of India (IRDAI), rather than internally measured empirical hospital processing SLAs.

---

## VIII. Conclusion

We presented an offline-capable, evidence-grounded intelligent assistant for cashless hospital verification and health insurance policy clause retrieval. By unifying FTS5 BM25 lexical indexing with a 128-dimensional feature-hashing dense channel via Reciprocal Rank Fusion, implementing heading-aware chunking with dual-page coordinate binding, enforcing deterministic evidence gating, and applying conservative spatial entity resolution, the system delivers verifiable, legally grounded guidance. Rigorous evaluations on real data establish baseline retrieval metrics (BM25 MRR 0.4379, Hybrid MiniLM MRR 0.4243), eliminate cross-jurisdiction hospital mismatching (100% test precision with strict location checks), and verify offline CPU execution.

---

## References

1. S. H. Hanmante, S. Patil, P. V. Deshmukh, and A. K. Shahade, "InsuranceRAG: A multi-module retrieval-augmented AI system for intelligent insurance assistance," *Software Impacts*, vol. 28, Art. no. 100844, 2026.
2. L. Wei et al., "InsQABench: Benchmarking Chinese insurance-domain question answering with large language models," *Inf. Process. Manage.*, vol. 63, no. 5, Art. no. 104685, 2026.
3. L. M. Amugongo et al., "Retrieval augmented generation for large language models in healthcare: A systematic review," *PLOS Digit. Health*, vol. 4, no. 6, Art. no. e0000877, 2025.
4. Y. Miao, Y. Zhao, Y. Luo, H. Wang, and Y. Wu, "Improving large language model applications in the medical and nursing domains with retrieval-augmented generation: Scoping review," *J. Med. Internet Res.*, vol. 27, Art. no. e80557, 2025.
5. C. M. Fensore, R. M. Carrillo-Larco, M. Shah, and J. C. Ho, "Does domain-specific retrieval augmented generation help LLMs answer consumer health questions?" in *Proc. 10th Mach. Learn. Healthcare Conf.*, PMLR, vol. 298, 2025.
6. G. Xiong, Q. Jin, Z. Lu, and A. Zhang, "Benchmarking retrieval-augmented generation for medicine," in *Findings Assoc. Comput. Linguistics: ACL 2024*, pp. 6233–6251, 2024.
7. S. Jeong, J. Baek, S. Cho, S. J. Hwang, and J. Park, "Adaptive-RAG: Learning to adapt retrieval-augmented large language models through question complexity," in *Proc. NAACL*, pp. 7036–7050, 2024.
8. A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, "Self-RAG: Learning to retrieve, generate, and critique through self-reflection," in *Proc. ICLR*, 2024.
9. S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, "Corrective retrieval augmented generation," *arXiv:2401.15884*, 2024.
10. A. Singh, A. Ehtesham, S. Kumar, T. T. Khoei, and A. V. Vasilakos, "Agentic retrieval-augmented generation: A survey on agentic RAG," *arXiv:2501.09136*, 2025.
11. D. Edge et al., "From local to global: A Graph RAG approach to query-focused summarization," *arXiv:2404.16130*, 2024.
12. S. Es, J. James, L. Espinosa Anke, and S. Schockaert, "RAGAs: Automated evaluation of retrieval augmented generation," in *Proc. EACL*, pp. 150–158, 2024.
13. J. Saad-Falcon, O. Khattab, C. Potts, and M. Zaharia, "ARES: An automated evaluation framework for retrieval-augmented generation systems," in *Proc. NAACL*, pp. 338–354, 2024.
14. C. Niu et al., "RAGTruth: A hallucination corpus for developing trustworthy retrieval-augmented language models," in *Proc. 62nd ACL*, pp. 10862–10878, 2024.
15. G. Yona, R. Aharoni, and M. Geva, "Can large language models faithfully express their intrinsic uncertainty in words?" in *Proc. EMNLP*, pp. 7752–7764, 2024.
16. Z. Wang et al., "HealthQ: Unveiling questioning capabilities of LLM chains in healthcare conversations," *Smart Health*, vol. 36, Art. no. 100570, 2025.
17. S. Wind et al., "Multi-step retrieval and reasoning improves radiology question answering with large language models," *npj Digit. Med.*, vol. 8, Art. no. 790, 2025.
18. A. Chakraborty, C. Dahal, and V. Gupta, "Federated retrieval-augmented generation: A systematic mapping study," in *Findings EMNLP*, pp. 7362–7374, 2025.
19. L. He, P. Tang, Y. Zhang, P. Zhou, and S. Su, "Mitigating privacy risks in retrieval-augmented generation via locally private entity perturbation," *Inf. Process. Manage.*, vol. 62, no. 4, Art. no. 104150, 2025.
20. X. Zhong et al., "Considerations for patient privacy of large language models in health care: Scoping review," *J. Med. Internet Res.*, vol. 27, Art. no. e76571, 2025.
21. S. Robertson and H. Zaragoza, "The probabilistic relevance framework: BM25 and beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–381, 2009.
22. G. V. Cormack, C. L. Clarke, and S. Buettcher, "Reciprocal rank fusion outperforms Condorcet and individual rank learning methods," in *Proc. 32nd ACM SIGIR*, pp. 758–759, 2009.
23. N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP*, 2019.
24. Insurance Regulatory and Development Authority of India (IRDAI), "Master Circular on Standardization of Health Insurance Contracts," Ref: IRDAI/HLT/REG/CIR/193/07/2024, New Delhi, India.
25. Ministry of Law and Justice, Government of India, "Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)," *The Gazette of India*, Aug. 2023.
