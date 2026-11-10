# AI-Assisted Health Insurance Intelligence Platform
## Complete Technical Reference

> **Purpose**: This document is raw technical material for crafting a research paper.  
> It describes every system component with exact parameters, data sources, and results as they exist in the codebase — unparaphrased and unedited for brevity.

---

## Table of Contents

1. [Project Motivation & Problem Statement](#1-project-motivation--problem-statement)
2. [Real-World Use Case](#2-real-world-use-case)
3. [System Overview](#3-system-overview)
4. [Datasets](#4-datasets)
5. [Database Schema](#5-database-schema)
6. [Data Ingestion Pipeline](#6-data-ingestion-pipeline)
7. [RAG Architecture](#7-rag-architecture)
8. [LLM Provider Chain](#8-llm-provider-chain)
9. [Hospital Network Status Determination](#9-hospital-network-status-determination)
10. [Backend API Design](#10-backend-api-design)
11. [Frontend Architecture](#11-frontend-architecture)
12. [Data Flow Diagrams](#12-data-flow-diagrams)
13. [Evaluation Metrics & Results](#13-evaluation-metrics--results)
14. [Configuration Parameters](#14-configuration-parameters)
15. [Technology Stack & Dependencies](#15-technology-stack--dependencies)
16. [Limitations & Known Constraints](#16-limitations--known-constraints)

---

## 1. Project Motivation & Problem Statement

### The Problem

Health insurance in India is notoriously opaque. When a policyholder is hospitalized, they face three simultaneous knowledge gaps:

1. **Policy comprehension gap**: Policy wording documents (48 pages, dense legalese) contain exact clauses about waiting periods, sub-limits, exclusions, and pre-/post-hospitalization coverage. Most policyholders cannot navigate these efficiently during a medical crisis.

2. **Hospital network uncertainty**: Patients need to verify whether a specific hospital is in the insurer's cashless network before choosing it for treatment. The authoritative directory requires internet and navigation skill. Offline or cached copies are geographically fragmentary.

3. **Claims process illiteracy**: The procedural steps for submitting cashless, reimbursement, document-upload, and status-check requests differ from each other and from what policyholders expect. Mistakes at any step cause delays or rejections.

### What Does Not Exist

- No open-source tool retrieves and cites exact insurance policy clauses in response to natural-language questions.
- No system cross-references a national government hospital registry with insurer-specific cashless network data while clearly disclosing the provenance and completeness limitations of each source.
- No system enforces strict abstention (refusing to answer) rather than hallucinating insurance terms that do not appear in verified source documents.

### What This Platform Provides

A locally-runnable, privacy-preserving intelligence platform that:

- Answers natural-language policy questions with **exact, cited passages** from verified source PDFs.
- Searches **29,974 government-registered hospitals** nationwide with partial, case-insensitive name matching.
- Cross-references hospital directory results against an **offline Star Health cashless network sample** and reports one of three clearly defined statuses.
- Provides step-by-step claims procedure guidance sourced from official Star Health and IRDAI web documents.
- **Strictly abstains** rather than generating unverified insurance claims.

---

## 2. Real-World Use Case

### Primary Scenario: Pre-Hospitalization Planning

A Star Health policyholder in Karnataka needs elective surgery. They want to know:

1. Does the policy cover this procedure, and under what waiting period?
2. Is the local hospital (e.g., "Manipal") a cashless network hospital?
3. What documents must be submitted for the cashless claim?

They enter a natural-language question → the system retrieves exact policy passages, cites page/section numbers from the verified PDF, searches the national hospital directory, checks against the Star Health Bangalore sample, and provides claims guidance — all without calling a cloud API or sharing patient data.

### Secondary Scenario: Post-Claim Dispute

A policyholder whose claim was partially rejected wants to verify what the policy actually says about "room rent" or "ICU sub-limits." The system retrieves the verbatim clause from the policy wording with its physical page number and section heading, so the user can cross-check against the official document.

---

## 3. System Overview

```
+--------------------------- HEALTH INSURANCE INTELLIGENCE PLATFORM ---------------------------+
|                                                                                               |
|  FRONTEND (React/TypeScript, Vite)                BACKEND (FastAPI/Python)                   |
|  +-------------------------+                      +------------------------------+            |
|  |  HomePage               |<------------------->|  /api/v1/health              |            |
|  |  PolicyQA               |                     |  /api/v1/qa/ask              |            |
|  |  PolicySearch           |<------------------->|  /api/v1/documents/          |            |
|  |  HospitalExplorer       |<------------------->|  /api/v1/hospitals/          |            |
|  |  ClaimsGuidance         |                     |  /api/v1/dashboard/summary   |            |
|  |  DocumentLibrary        |                     +------------------------------+            |
|  +-------------------------+                                 |                               |
|                                                              v                               |
|                                               +------------------------------+               |
|   DATA LAYER                                  |  RAG PIPELINE               |               |
|  +----------------------+                     |  +------------------------+ |               |
|  |  SQLite DB           |<------------------->|  |  SQLite FTS5 (BM25)    | |               |
|  |  hospitals (29,974)  |                     |  +------------------------+ |               |
|  |  insurer_records(10) |                     |  |  LocalVectorStore      | |               |
|  |  documents (7)       |                     |  |  (cosine, 128-dim)     | |               |
|  |  document_chunks(263)|                     |  +------------------------+ |               |
|  |  conversations       |                     |  |  RRF Fusion            | |               |
|  |  messages            |                     |  |  alpha=0.5, k=60       | |               |
|  +----------------------+                     |  +------------------------+ |               |
|                                               |  |  LLM Provider          | |               |
|  +----------------------+                     |  |  Ollama/OpenAI/Gemini/ | |               |
|  |  vector_index.json   |<------------------->|  |  Fallback Extractive   | |               |
|  |  263 x 128-dim vecs  |                     |  +------------------------+ |               |
|  +----------------------+                     +------------------------------+               |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Datasets

### 4.1 National Government Hospital Directory

| Property | Value |
|---|---|
| **File** | `data/hospitals/hospital_directory.csv` |
| **File Size** | 10,341,256 bytes (~9.9 MB) |
| **Source** | National Health Authority (NHA) public hospital registry |
| **Format** | CSV with UTF-8/Latin-1 encoding |
| **Total Rows in CSV** | 30,273 rows (including header) |
| **Rows Imported** | 29,974 valid records |
| **Rows Skipped** | 299 (empty hospital names, placeholder "0" values) |
| **Geographic Coverage** | All Indian states and union territories |

**Fields in the CSV (mapped to database columns):**

| CSV Column | DB Column | Notes |
|---|---|---|
| `Hospital_Name` | `hospital_name` | Required; indexed |
| `State` | `state` | Indexed |
| `District` | `district` | Indexed |
| `Subdistrict` | `subdistrict` | |
| `Pincode` | `pincode` | Indexed |
| `Hospital_Category` | `hospital_category` | Government, Private, etc. |
| `Hospital_Care_Type` | `care_type` | Primary, Secondary, Tertiary |
| `Discipline_Systems_of_Medicine` | `discipline` | Allopathy, Ayurveda, etc. |
| `Address_Original_First_Line` + `Location` | `address` | Combined into one field |
| `Location_Coordinates` | `latitude`, `longitude` | Parsed as float pair |
| `Total_Num_Beds` | `total_beds` | Parsed as integer |
| `Specialties` | `specialties` | Free text |
| `Telephone`, `Mobile_Number` | `telephone`, `mobile_number` | |
| `Emergency_Num` | `emergency_num` | |
| `Ambulance_Phone_No` | `ambulance_phone` | |
| `Bloodbank_Phone_No` | `bloodbank_phone` | |
| `Hospital_Primary_Email_Id` | `email` | |
| `Website` | `website` | |

**Example Record** (Kerudi Hospital, Bagalkot, Karnataka):
```
hospital_name : "Kerudi Hospital And Research Centre"
state         : "Karnataka"
district      : "Bagalkot"
pincode       : "587101"
```

**Duplicate Prevention**: Idempotency key = `(hospital_name.lower(), state.lower(), pincode)`. On re-ingestion, matching keys are skipped.

**Coordinate Validation**: Parsed lat/lon are validated against bounds [-90, 90] x [-180, 180] before insertion.

---

### 4.2 Star Health Insurer Network (Bangalore Sample)

| Property | Value |
|---|---|
| **File 1** | `data/insurer_networks/...Bangalore...htm` (717,017 bytes) |
| **File 2** | `data/insurer_networks/...Bangalore...mhtml` (1,650,504 bytes) |
| **Source** | Star Health and Allied Insurance Company website (offline save) |
| **Source URL** | `https://www.starhealth.in/network-hospitals/star-health-network-hospitals-list-in-bangalore-karnataka/` |
| **Geographic Coverage** | Bengaluru (Bangalore) city only |
| **Records Extracted** | 10 unique hospital cards (deduplicated across HTML + MHTML) |
| **Records Imported** | 10 `insurer_hospital_records` rows |
| **Duplicates Skipped** | 10 (same hospitals appear in both copies) |
| **Directory Links** | 6 of 10 confidently linked to `hospitals` table via normalized name + pincode match |

**HTML Structure Parsed**: Each hospital card is a `<div>` with CSS classes `["border", "rounded-md", "p-4"]`. Within the card:
- Title: `<div class="font-semibold">` → `hospital_name`
- Pincode: Regex `\b(560\d{3})\b` applied to all text strings
- Address: First string containing `"road"`, `"cross"`, `"main"`, `"layout"`, `"nagar"`, `"street"`, `"opp"`, `"no."`, or `"#"`
- Phone: Regex `\b\d{3,5}\s*-\s*\d{6,8}\b`
- Network type: `"Cashless Network"` if `"Network Hospital"` in text, else `"Cashless"`

**Data Completeness Caveat**: This is an incomplete offline snapshot. It captures hospitals that appeared on the Star Health Bangalore page at the time of the save. It does NOT represent the complete Star Health national network. This limitation is explicitly disclosed in every relevant API response and frontend UI element.

---

### 4.3 Policy Documents (RAG Source)

| Document | File | DB Type | Size | Pages | Chunks |
|---|---|---|---|---|---|
| Star Comprehensive Insurance Policy - Terms & Conditions Wording | `Policy_Star_Comprehensive_Insurance_Policy_clean.pdf` | `policy` | 2,101,643 bytes | 48 physical | 179 |
| Star Comprehensive Insurance Policy - Customer Information Sheet (CIS) | `CIS_Star_Comprehensive_Insurance_Policy_V_2_69c15a9ee1.pdf` | `cis` | 1,671,059 bytes | 20 physical | 60 |
| Legacy Policy PDF (superseded) | `Policy_Star_..._V_21_...pdf` | — | 3,572,004 bytes | — | Skipped |

**Document Identifiers**:
- Policy UIN: `SHAHLIP26044V092526`
- Policy Version: `POL / COMP / V.24 / 2025`
- CIS Version: `V.2 / 2025`

**Page Numbering Convention**:
- Full Policy: Physical page 1 = unnumbered cover sheet; printed pages run 1/47 through 47/47 on physical pages 2-48.
- CIS: Physical page 1 = cover; printed pages 1/19 through 19/19 on physical pages 2-20.
- The system stores both `page_number` (physical, 1-indexed) and `printed_page_number` (physical - 1) and generates human-readable labels like `"Physical Page 9 (Printed Page 8/19)"`.

---

### 4.4 Claim Guidance Documents (RAG Source)

| Document | File | DB Type | Size | Chunks |
|---|---|---|---|---|
| IRDAI Health Insurance FAQs | `irdai_health_insurance_faqs.mhtml` | `faq` | 2,015,607 bytes | 16 |
| Star Cashless Claims Guide | `star_cashless_claims.mhtml` | `claim_guidance` | 790,120 bytes | 2 |
| Star Claim Document Upload Guide | `star_claim_document_upload.mhtml` | `claim_guidance` | 790,161 bytes | 2 |
| Star Claim Status Guide | `star_claim_status.mhtml` | `claim_guidance` | 789,316 bytes | 2 |
| Star Reimbursement Claims Guide | `star_reimbursement_claims.mhtml` | `claim_guidance` | 790,168 bytes | 2 |

**Total across all document types**: 7 documents, 263 chunks, ~247,000 characters of indexed text.

---

## 5. Database Schema

**Engine**: SQLite (file: `health_insurance.db`, 11,247,616 bytes)
**ORM**: SQLAlchemy 2.x with declarative base
**Foreign Keys**: Enforced via `PRAGMA foreign_keys=ON` on every connection

### Table: `hospitals`

```
hospitals
  id                INTEGER  PK AUTOINCREMENT
  sr_no             VARCHAR(50) NULL
  hospital_name     VARCHAR(255) NOT NULL  [INDEX]
  hospital_category VARCHAR(100) NULL
  care_type         VARCHAR(100) NULL
  discipline        VARCHAR(100) NULL
  address           TEXT NULL
  state             VARCHAR(100) NULL  [INDEX]
  district          VARCHAR(100) NULL  [INDEX]
  subdistrict       VARCHAR(100) NULL
  pincode           VARCHAR(20) NULL   [INDEX]
  telephone         VARCHAR(100) NULL
  mobile_number     VARCHAR(100) NULL
  emergency_num     VARCHAR(100) NULL
  ambulance_phone   VARCHAR(100) NULL
  bloodbank_phone   VARCHAR(100) NULL
  email             VARCHAR(255) NULL
  website           VARCHAR(255) NULL
  specialties       TEXT NULL
  facilities        TEXT NULL
  total_beds        INTEGER NULL
  latitude          FLOAT NULL
  longitude         FLOAT NULL
  created_at        DATETIME NOT NULL DEFAULT NOW
  updated_at        DATETIME NOT NULL DEFAULT NOW
  -- Relationship: insurer_records -> InsurerHospitalRecord[] (cascade delete-orphan)
```

### Table: `insurer_hospital_records`

```
insurer_hospital_records
  id                   INTEGER  PK AUTOINCREMENT
  insurer_name         VARCHAR(100) NOT NULL DEFAULT "Star Health"  [INDEX]
  hospital_name        VARCHAR(255) NOT NULL  [INDEX]
  city                 VARCHAR(100) NULL  [INDEX]
  state                VARCHAR(100) NULL  [INDEX]
  pincode              VARCHAR(20) NULL   [INDEX]
  address              TEXT NULL
  network_type         VARCHAR(50) DEFAULT "Cashless" NULL
  raw_details          TEXT NULL  -- JSON: {phone, source_url, source_file}
  matched_hospital_id  INTEGER NULL FK->hospitals.id (SET NULL on delete)  [INDEX]
  created_at           DATETIME NOT NULL DEFAULT NOW
  updated_at           DATETIME NOT NULL DEFAULT NOW
  -- Relationship: matched_hospital -> Hospital (nullable FK)
```

### Table: `documents`

```
documents
  id              INTEGER  PK AUTOINCREMENT
  title           VARCHAR(255) NOT NULL  [INDEX]
  document_type   VARCHAR(50) NOT NULL   [INDEX]  -- policy|cis|claim_guidance|faq
  source_path     VARCHAR(500) NOT NULL UNIQUE
  file_format     VARCHAR(20) NOT NULL   -- pdf|html|mhtml
  file_size_bytes INTEGER NULL
  version         VARCHAR(50) NULL
  metadata_json   TEXT NULL  -- JSON blob with extraction stats
  is_processed    BOOLEAN NOT NULL DEFAULT FALSE  [INDEX]
  created_at      DATETIME NOT NULL DEFAULT NOW
  updated_at      DATETIME NOT NULL DEFAULT NOW
  -- Relationship: chunks -> DocumentChunk[] (ordered by chunk_index)
```

### Table: `document_chunks`

```
document_chunks
  id              INTEGER  PK AUTOINCREMENT
  document_id     INTEGER NOT NULL FK->documents.id (CASCADE)  [INDEX]
  text            TEXT NOT NULL     -- raw extracted text, 800-1000 chars
  page_number     INTEGER NULL      -- physical PDF page (1-indexed)
  section_heading VARCHAR(255) NULL -- detected section label
  chunk_index     INTEGER NOT NULL  -- ordering within document
  content_hash    VARCHAR(64) NOT NULL  [INDEX]  -- SHA-256 of text
  token_count     INTEGER NULL      -- whitespace token count
  created_at      DATETIME NOT NULL DEFAULT NOW
  -- UNIQUE (document_id, chunk_index) [uq_doc_chunk_index]
```

### Virtual Table: `document_chunks_fts` (SQLite FTS5)

```
document_chunks_fts
  chunk_id      UNINDEXED  -- reference to document_chunks.id
  document_id   UNINDEXED  -- reference to documents.id
  text          (full-text indexed)
  section_heading (full-text indexed)

  tokenize = 'porter unicode61'
  Ranking: BM25 via bm25() builtin
  Snippet: snippet(col=2, open='<b>', close='</b>', ellipsis='...', window=32)
```

### Tables: `conversations`, `messages`

```
conversations
  id          VARCHAR(36) PK  -- UUID string
  title       VARCHAR(80) NULL
  created_at  DATETIME

messages
  id               INTEGER  PK AUTOINCREMENT
  conversation_id  VARCHAR(36) FK->conversations.id (CASCADE)
  role             VARCHAR(20)  -- "user" | "assistant"
  content          TEXT
  citations        TEXT NULL    -- JSON array of CitationItem dicts
  created_at       DATETIME
```

---

## 6. Data Ingestion Pipeline

### 6.1 Pipeline Execution Order (`scripts/ingest_all.py`)

```
Step 1: ingest_hospitals.py
  hospital_directory.csv --> hospitals table
  Batch size: 2,000 rows per commit
  Encoding: UTF-8-sig -> UTF-8 -> Latin-1 (fallback cascade)
  Idempotency key: (name.lower, state.lower, pincode)

Step 2: ingest_insurer_networks.py
  *.htm / *.html / *.mhtml --> insurer_hospital_records table
  HTML parser: BeautifulSoup4
  MHTML parser: email.message_from_binary_file()
  Normalization: NFKD ASCII + stopword pruning
  Directory linking: SequenceMatcher ratio >= 0.94 + locality match

Step 3: ingest_policies.py
  *.pdf --> documents + document_chunks
  Primary extractor: pypdf
  Fallback extractor: PyMuPDF (fitz)
  Chunking: sliding window 800-1000 chars + 1-line overlap
  FTS5 sync: sync_fts5_index() called after all chunks are saved

Step 4: ingest_claim_guidance.py
  *.mhtml --> documents + document_chunks
  Parser: BeautifulSoup4 (html.parser)
  Heading detection: <h1>, <h2>, <h3>, <h4> tags
  Content: <p>, <li>, <dt>, <dd> tags
  Chunking: accumulate until >= 800 chars, then emit

Step 5: sync_fts5_index()  [search.py]
  SELECT all document_chunks -> INSERT INTO document_chunks_fts
  Clears and rebuilds the entire FTS5 index

Step 6: index_all_chunks()  [index_embeddings.py]
  SELECT all document_chunks -> embed -> vector_index.json
  Embedding input: f"{doc_title} {section_heading} {text}"
  Provider: LocalDenseEmbeddingProvider (128-dim)
  Save: atomic JSON write via tempfile + os.replace()
```

### 6.2 Hospital Name Normalization (Canonical Form)

Used identically in both `hospitals.py` (API) and `ingest_insurer_networks.py` (ingestion):

```python
def normalize_hospital_name(value: str) -> str:
    # 1. Replace & -> " and ", strip apostrophes
    val = value.replace("&", " and ").replace("'", "").replace("\u2019", "")
    # 2. NFKD Unicode normalization + ASCII transliteration
    normalized = unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode("ascii")
    # 3. Tokenize: only alphanumeric tokens, lowercase
    tokens = re.findall(r"[a-z0-9]+", normalized.lower())
    # 4. Pluralization: "hospitals" -> "hospital"
    tokens = ["hospital" if token == "hospitals" else token for token in tokens]
    # 5. Strip trailing legal suffixes
    while tokens and tokens[-1] in {"pvt", "private", "ltd", "limited", "llp", "inc"}:
        tokens.pop()
    return " ".join(tokens)
```

**Examples**:

| Input | Normalized Output |
|---|---|
| `"BANGALORE BAPTIST HOSPITAL"` | `"bangalore baptist hospital"` |
| `"Kerudi Hospital & Research Centre"` | `"kerudi hospital and research centre"` |
| `"Chaitanya Hospital Pvt Ltd"` | `"chaitanya hospital"` |
| `"Apollo Hospitals - Bangalore"` | `"apollo hospital bangalore"` |
| `"St. John's Hospital"` | `"st johns hospital"` |

**Conservative Non-Matching** (these normalize to DIFFERENT strings):

| Input A | Input B |
|---|---|
| `"Aditi Eye Care"` | `"Aditi Nursing Home"` |
| `"Manipal Northside Hospital"` | `"Manipal Hospital"` |
| `"Apollo Clinic"` | `"Apollo Hospitals"` |

---

## 7. RAG Architecture

### 7.1 Overview Diagram

```
USER QUESTION
     |
     v
+------------------------------------------------------+
|  QUERY PREPROCESSING  (services/qa.py)              |
|  - Strip whitespace                                  |
|  - Extract meaningful keywords (stopword-filtered)   |
|  - Phrase expansion:                                 |
|    "before hospitalization" -> "prehospitalization" |
|    "after hospitalization"  -> "posthospitalization"|
+------------------------------------------------------+
     |
     +-----------------------------+
     |                             |
     v                             v
+------------------+    +---------------------+
|  BM25 SEARCH     |    |  VECTOR SEARCH      |
|  (FTS5)          |    |  (LocalVectorStore) |
|                  |    |                     |
|  Tier 1: AND     |    |  embed query        |
|  Tier 2: OR      |    |  -> 128-dim vector  |
|  top_k * 2 items |    |  -> cosine sim dot  |
|                  |    |  -> top_k * 2 items |
+------------------+    +---------------------+
     |                             |
     +-----------------------------+
               |
               v
+--------------------------------------------------+
|  RECIPROCAL RANK FUSION (RRF)                    |
|  (services/retrieval.py)                         |
|                                                  |
|  RRF_score(chunk) =                              |
|    alpha / (k + bm25_rank + 1)                   |
|  + (1 - alpha) / (k + vector_rank + 1)           |
|                                                  |
|  alpha = 0.5  (BM25 weight)                      |
|  k = 60.0     (smoothing constant)               |
|                                                  |
|  Deduplication by chunk_id                       |
|  Sort descending by RRF score                    |
|  Return top_k (default 5)                        |
+--------------------------------------------------+
               |
               v
+--------------------------------------------------+
|  RELEVANCE FILTER  (services/qa.py)              |
|                                                  |
|  keywords = extract_meaningful_keywords(q)       |
|  required_matches = 2 if len(kw) >= 3 else 1    |
|                                                  |
|  For each chunk:                                 |
|    content = heading + text + excerpt            |
|    if count(kw in content) >= required_matches:  |
|      -> valid citation                           |
+--------------------------------------------------+
               |
     +---------+---------+
     |                   |
     v                   v
Citations exist?    No citations
     |                   |
     v                   v
+------------+  +------------------------------+
| LLM call   |  | STRICT ABSTENTION            |
| (optional) |  | status="insufficient_evid." |
|            |  | is_sufficient_evidence=false |
| Ollama /   |  | citations=[]                 |
| OpenAI /   |  | "I cannot verify..."         |
| Gemini /   |  +------------------------------+
| Fallback   |
+------------+
     |
     v
+--------------------------------------------------+
|  RESPONSE CONSTRUCTION                           |
|  - LLM answer (if available) + source lines      |
|  - OR extractive synthesis from passages         |
|  - + mandatory disclaimer text                   |
|  - + NETWORK_STATUS_CLARIFICATION (if question   |
|    contains "hospital", "network", "cashless",   |
|    or "directory")                               |
|  - Persist to conversations + messages           |
+--------------------------------------------------+
               |
               v
        QuestionResponse JSON
```

---

### 7.2 Text Chunking Strategy

**Location**: `scripts/ingest_policies.py` -> `extract_headings_and_chunks()`

#### Algorithm

```
INPUT: Page text (extracted by pypdf or PyMuPDF)

Step 1: Line splitting and stripping
  raw_lines = text.split("\n"), strip each line, remove empty

Step 2: Header/footer artifact removal
  Remove lines matching: r"^\d+\s*/\s*47$"   (e.g. "12 / 47")
  Remove lines containing both "STAR HEALTH AND ALLIED..." and "POLICY WORDINGS"
  Remove lines containing both "SHAHLIP26044V092526" and "V.24 / 2025"

Step 3: Section heading detection
  A line is treated as a section heading if ALL true:
    len(line) < 80
    NOT starts with "Note:"
    ONE of:
      line.isupper()
      matches r"^(section|clause|part|table|item|coverage|benefit|
                   exclusion|condition|preamble|definitions)\b" (case-insensitive)
      line.endswith(":")
  -> current_heading = line.rstrip(":")

Step 4: Chunk accumulation with overlap
  current_chunk_lines = []
  for each line:
    current_chunk_lines.append(line)
    joined_text = " ".join(current_chunk_lines)
    if len(joined_text) >= 800:              <- CHUNK THRESHOLD
      content_hash = SHA-256(joined_text)
      emit chunk(text, page_num, current_heading, chunk_index, hash, token_count)
      current_chunk_lines = current_chunk_lines[-1:]  <- 1-LINE OVERLAP

Step 5: Trailing chunk
  if remaining text > 30 chars: emit final chunk

Step 6: Content hash
  SHA-256(chunk_text.encode("utf-8")).hexdigest()  -> 64-char hex

Step 7: Token count
  len(chunk_text.split())  [whitespace tokenization]
```

#### Chunk Parameters (Exact Values)

| Parameter | Value |
|---|---|
| Chunk target size | 800 characters minimum (soft ceiling ~1000 chars) |
| Overlap strategy | 1-line carryover: `current_chunk_lines[-1:]` |
| Overlap size (approx) | 20-40 tokens (~80-120 characters) |
| Minimum trailing chunk | 30 characters |
| Minimum claim guidance chunk | 50 characters |
| Hash algorithm | SHA-256, hexdigest (64 chars) |
| Token count method | Whitespace split |

#### Resulting Statistics

| Source | Pages | Chunks | Chars indexed |
|---|---|---|---|
| Full Policy PDF | 48 | 179 | 134,147 |
| CIS PDF | 20 | 60 | 39,754 |
| IRDAI FAQ MHTML | 1 | 16 | 38,029 |
| 4x Claim Guidance MHTMLs | 4 | 8 | 35,307 |
| **Total** | **--** | **263** | **~247,237** |

---

### 7.3 Embedding Model

**Configuration key**: `EMBEDDING_PROVIDER = "local"`
**Class**: `LocalDenseEmbeddingProvider` (`backend/app/services/embeddings.py`)

#### Architecture

A custom zero-dependency embedding model based on:
1. **Word tokens and bigrams** -- weighted 1.5 for unigrams, 1.0 for bigrams
2. **Character 4-grams** -- weighted 0.4 for morphological coverage
3. **Subword polynomial hashing** -- each token hashed to a dimension index
4. **L2 normalization** -- unit-length output vector

#### Hashing Function

```python
def _hash_token(self, token: str) -> int:
    h = 0
    for char in token:
        h = (h * 31 + ord(char)) & 0xFFFFFFFF
    return h % self.vector_dim   # vector_dim = 128
```

Polynomial rolling hash (multiplier = 31) over character ordinals, bounded to [0, 127].

#### Embedding Computation

```
text -> lowercase
-> word tokens (regex: \b[a-z0-9]+\b)
   for word w (len >= 2):
     vec[hash(w)] += 1.5
     if i < len(words)-1:
       vec[hash(f"{w}_{words[i+1]}")] += 1.0   (bigram)
-> character 4-grams over full text:
   for i in range(len(text) - 3):
     sub = text[i:i+4]
     vec[hash(sub)] += 0.4
-> L2 normalize: vec = vec / ||vec||_2
-> output: List[float], length = 128
```

#### Properties

| Property | Value |
|---|---|
| Output dimension | 128 |
| Normalization | L2 (unit sphere) |
| Deterministic | Yes |
| External dependencies | NumPy only |
| Computation device | CPU only |

**Optional upgrade**: `SentenceTransformersEmbeddingProvider` available. Falls back to local if import fails. Configured via `EMBEDDING_PROVIDER = "sentence-transformers"`, `EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"`.

#### Embedding Input Construction

```python
text_to_embed = f"{doc_title} {chunk.section_heading or ''} {chunk.text}"
```

Document title and section heading are prepended to each chunk so that semantic similarity includes document-level context.

---

### 7.4 Vector Store

**Class**: `LocalVectorStore` (`backend/app/services/vector_store.py`)
**Persistence**: `vector_index.json` (1,016,990 bytes)

#### File Format

```json
{
  "version": "1.0",
  "count": 263,
  "vectors": [[...128 floats...], ...],
  "metadata": [
    {
      "chunk_id": 1,
      "document_id": 1,
      "document_title": "Star Comprehensive Insurance Policy - Terms & Conditions Wording",
      "document_type": "policy",
      "version": "POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)",
      "page_number": 2,
      "printed_page_number": 1,
      "page_label": "Physical Page 2 (Printed Page 1/47)",
      "section_heading": "PREAMBLE",
      "supporting_text": "...",
      "content_hash": "..."
    }
  ]
}
```

Document types present in vector index: `policy`, `cis`, `claim_guidance`, `faq`.

#### Search Method

```python
similarities = np.dot(matrix, q_vec)   # matrix: (263, 128), q_vec: (128,)
```

Since all vectors are L2-normalized, `dot(a, b) = cosine_similarity(a, b)`.

**Persistence**: Saved atomically via `tempfile.NamedTemporaryFile` + `os.replace()`.

---

### 7.5 BM25 Full-Text Search (FTS5)

**Engine**: SQLite FTS5 virtual table
**Tokenizer**: `porter unicode61` (Porter stemmer + Unicode-aware tokenization)

#### Query Strategy (Two-Tier)

```python
# Tier 1: Strict AND query - all meaningful tokens must appear
q_and = " AND ".join([f'"{w}"' for w in tokens])
rows = db.execute(fts_sql, {"query": q_and, ...})

# Tier 2: Broaden with OR if AND returns < limit results
if len(rows) < limit and len(tokens) > 1:
    q_or = " OR ".join([f'"{w}"' for w in tokens])
    # Append de-duplicated OR results to AND results
```

**Ranking**: `bm25(document_chunks_fts)` native SQLite BM25.
**Order**: `ORDER BY rank` (BM25 score; SQLite returns negative values, lower = better).

#### Query Preprocessing

```
STOPWORDS = {
  "what", "is", "the", "for", "are", "about", "does", "say", "to",
  "of", "in", "and", "a", "an", "policy", "tell", "me", "how",
  "can", "do", "it", "any", "which", "with", "from", "on", "under",
  "this", "that", "these", "those", "have", "has", "had", "be",
  "been", "being", "there", "cover", "covered", "coverage", "says",
  "mean", "means", "give", "gives", "before", "after", "related",
  "terms", "term", "high", "low", "provide", "provides", "provided",
  "details", "detail"
}

SPELLING_VARIANTS = {
  "hospitalisation": "hospitalization",
  "prehospitalisation": "prehospitalization",
  "organisation": "organization",
  "authorisation": "authorization"
}

Phrase expansion rules:
  "before hospitalization" -> "prehospitalization"
  "after hospitalization"  -> "posthospitalization"
  "prior to hospitalization" -> "prehospitalization"
```

#### Snippet Generation

```sql
snippet(document_chunks_fts, 2, '<b>', '</b>', '...', 32)
```

Column 2 = `text`. Snippets use HTML bold markers, 32-token window.

---

### 7.6 Reciprocal Rank Fusion

**Location**: `backend/app/services/retrieval.py`

#### Formula

```
RRF_score(chunk_i) = alpha / (k + rank_BM25(chunk_i) + 1)
                   + (1 - alpha) / (k + rank_vector(chunk_i) + 1)
```

- `alpha = 0.5` (BM25 weight; set via `RAG_HYBRID_ALPHA` in config)
- `k = 60.0` (smoothing constant; hardcoded in `retrieval.py`)
- `rank_BM25(i)` = 0-indexed rank in BM25 result list (best = 0)
- `rank_vector(i)` = 0-indexed rank in cosine similarity result list (best = 0)

If a chunk appears only in one result set, only the corresponding term is added.
Deduplication: keyed by `chunk_id`. Scores are summed for chunks appearing in both.

#### Retrieval Mode Labels

| BM25 results | Vector results | retrieval_mode label |
|---|---|---|
| yes | yes | `"hybrid"` |
| no | yes | `"vector"` |
| yes | no | `"keyword"` |

**Fallback**: If hybrid search raises any exception, falls back to plain BM25 and sets `retrieval_mode = "keyword"`.

---

### 7.7 Relevance Filtering

```python
keywords = extract_meaningful_keywords(clean_q)   # stopword-filtered tokens
required_matches = 2 if len(keywords) >= 3 else 1

for r in raw_results:
    full_content = (section_heading + full_text + supporting_text + excerpt).lower()
    matching_kw = [kw for kw in keywords if kw in full_content]
    if len(matching_kw) >= required_matches:
        is_relevant = True
        valid_citations.append(CitationItem(...))
```

If no citations pass: `status = "insufficient_evidence"` -> strict abstention.

---

### 7.8 Grounded Answer Construction (Fallback / No LLM)

When no LLM is available:

```
### Direct Policy Answer

- <passage 1 text>
- <passage 2 text>
...

**Sources:**
- <document_title> (Version: <version>)
...
```

---

## 8. LLM Provider Chain

**Location**: `backend/app/services/llm_provider.py`

### System Prompt

```
You are an assistant answering questions about the Star Health Comprehensive Insurance Policy.
Use only the supplied evidence passages. Distinguish policy terms from general guidance.
Include relevant limitations stated in the evidence. Never promise claim approval or invent
clauses, limits, waiting periods, quotations, or page numbers. If evidence is insufficient
or conflicting, say so. Format the response in Markdown with a direct answer and key
conditions when supported.
```

### Provider Priority Chain

```
get_llm_provider() resolves in this order:

1. LLM_PROVIDER in {"openai", "auto"} AND OPENAI_API_KEY is set:
   -> OpenAILLMProvider(model=LLM_MODEL_NAME, temp=0.2, max_tokens=600)

2. LLM_PROVIDER in {"gemini", "auto"} AND GEMINI_API_KEY is set:
   -> GeminiLLMProvider(model="gemini-1.5-flash", temp=0.2, max_tokens=600)

3. LLM_PROVIDER in {"ollama", "auto"}:
   -> OllamaLLMProvider(base_url=OLLAMA_BASE_URL="http://localhost:11434",
                         model=OLLAMA_MODEL_NAME="llama3.2")

4. Fallback:
   -> OpenAILLMProvider(api_key="")   -- always returns (None, "fallback")
   -> extractive synthesis used instead
```

**Default configuration**: `LLM_PROVIDER = "ollama"`, `OLLAMA_MODEL_NAME = "llama3.2"`.

### LLM Call Parameters

| Provider | Endpoint | Timeout | temperature | max_tokens |
|---|---|---|---|---|
| OpenAI | `POST /v1/chat/completions` | 15.0s | 0.2 | 600 |
| Gemini | `POST /v1beta/models/{model}:generateContent` | 15.0s | 0.2 | 600 |
| Ollama | `POST /api/chat` (stream=False) | 60.0s (connect=1.0s) | 0.2 | -- |

### Evidence Format Passed to LLM

```
Passage 1 ({document_title} - {page_label}):
{supporting_text}

Passage 2 ({document_title} - {page_label}):
{supporting_text}
```

---

## 9. Hospital Network Status Determination

**Location**: `backend/app/api/v1/hospitals.py` -> `determine_hospital_network_status()`

### Three-Status Model

| Status String | Condition | Frontend Display |
|---|---|---|
| `"Listed in Star Health network data"` | FK link or normalized name + location match in insurer table | Emerald badge |
| `"Not found in the imported network data"` | Insurer table non-empty, no match found | Amber badge + disclaimer |
| `"Network status not verified"` | `insurer_hospital_records` table is empty | Italic text |

### Algorithm

```python
def determine_hospital_network_status(hospital, insurer_records, total_insurer_records):
    # 1. Empty insurer dataset
    if total_insurer_records == 0:
        return "Network status not verified"

    # 2. Foreign-key relationship (direct DB link)
    if hospital.insurer_records and len(hospital.insurer_records) > 0:
        return "Listed in Star Health network data"
    for r in insurer_records:
        if r.matched_hospital_id == hospital.id:
            return "Listed in Star Health network data"

    # 3. Normalized name + location compatibility check
    norm_h = normalize_hospital_name(hospital.hospital_name)
    if not norm_h:
        return "Network status not verified"

    for r in insurer_records:
        norm_r = normalize_hospital_name(r.hospital_name)
        if norm_h == norm_r:
            if location_compatible(hospital.state, hospital.district, hospital.pincode,
                                   r.state, r.city, r.pincode):
                return "Listed in Star Health network data"

    # 4. No match found
    return "Not found in the imported network data"
```

### Location Compatibility Logic

```python
def location_compatible(h_state, h_district, h_pincode, r_state, r_city, r_pincode):
    # Direct pincode match (strongest signal)
    if h_pincode and r_pincode and h_pincode.strip() == r_pincode.strip():
        return True
    # State contradiction (explicit mismatch)
    if h_state and r_state:
        s1, s2 = h_state.strip().lower(), r_state.strip().lower()
        if s1 and s2 and s1 != s2 and s1 not in s2 and s2 not in s1:
            return False
    # City/district compatibility (Bengaluru/Bangalore alias handled)
    if r_city and h_district:
        c, d = r_city.strip().lower(), h_district.strip().lower()
        if ("bengaluru" in c or "bangalore" in c) and ("bengaluru" in d or "bangalore" in d):
            return True
        if c in d or d in c:
            return True
    # State-level match (weakest)
    if h_state and r_state:
        s1, s2 = h_state.strip().lower(), r_state.strip().lower()
        if s1 == s2 or s1 in s2 or s2 in s1:
            return True
    return True   # Default: no contradiction found
```

---

## 10. Backend API Design

**Framework**: FastAPI 0.110+
**Server**: Uvicorn
**Base URL**: `http://127.0.0.1:8000`
**API prefix**: `/api/v1`

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service identity |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |
| GET | `/api/v1/health` | Liveness probe |
| GET | `/api/v1/dashboard/summary` | DB counts + dataset file status |
| GET | `/api/v1/hospitals` | Paginated hospital directory |
| GET | `/api/v1/hospitals/{id}` | Single hospital by ID |
| GET | `/api/v1/hospitals/insurer-network` | Paginated insurer network records |
| GET | `/api/v1/documents` | Paginated document list |
| GET | `/api/v1/documents/{id}` | Single document |
| GET | `/api/v1/documents/{id}/chunks` | Document chunks |
| GET | `/api/v1/documents/search` | BM25 passage search |
| POST | `/api/v1/qa/ask` | RAG question answering |
| POST | `/api/v1/documents/ask` | Compatibility alias for /qa/ask |

### Hospital Search Parameters

| Parameter | Type | Description |
|---|---|---|
| `page` | int >= 1 | Page number (default 1) |
| `page_size` | int 1-100 | Items per page (default 20) |
| `search` | string | Partial, case-insensitive ILIKE match |
| `state` | string | Filter by state |
| `district` | string | Filter by district |
| `pincode` | string | Exact pincode match |
| `source` | string | `"govt"/"national"` = directory; `"insurer"/"star"` = insurer network |

### Error Response Envelope

```json
{
  "error": {
    "code": "HTTP_404 | VALIDATION_ERROR | INTERNAL_SERVER_ERROR",
    "message": "...",
    "details": null
  }
}
```

---

## 11. Frontend Architecture

**Framework**: React 18 + TypeScript
**Build tool**: Vite
**Styling**: Tailwind CSS
**HTTP client**: Fetch API (`frontend/src/api/client.ts`)

### Navigation Tabs

| Tab | Component | Description |
|---|---|---|
| `home` | `HomePage.tsx` | Landing page with quick-search |
| `policy` | `PolicyInformationPage.tsx` | PolicyQA + PolicySearch |
| `hospitals` | `HospitalExplorer.tsx` | Two-tab hospital explorer |
| `claims` | `ClaimsGuidance.tsx` | Step-by-step claims guides |
| `documents` | `DocumentLibrary.tsx` | Document explorer |

### Key Frontend Features

**`HospitalExplorer.tsx`**:
- Two source tabs: `'govt'` (National Directory) / `'insurer'` (Star Health Network)
- `insurerTotalCount`: fetched dynamically on mount via `fetchInsurerHospitals({ page:1, pageSize:1, source:'insurer' })`
- State filter (`stateFilter`) applied on both tabs
- Three distinct network status badges with appropriate disclaimers

**`PolicyQA.tsx`**:
- 6 sample question chips for quick testing
- Calls `POST /api/v1/qa/ask`
- Citation accordion with page number, section heading, supporting text
- Abstention banner when `is_sufficient_evidence = false`
- Copy-to-clipboard for answer text
- Renders markdown via `MarkdownView.tsx`

**`PolicySearch.tsx`**:
- Direct BM25 passage search via `GET /api/v1/documents/search?q=...`
- Document type filter: All | Policy | CIS | Claims Guidance | IRDAI FAQ
- Highlighted excerpts with `<b>` tags

---

## 12. Data Flow Diagrams

### 12.1 Full Ingestion Pipeline

```
[hospital_directory.csv]           [insurer_networks/*.htm /*.mhtml]
       |                                          |
       v                                          v
 ingest_hospitals.py                  ingest_insurer_networks.py
  parse CSV (3 encoding fallbacks)      BeautifulSoup4 card extraction
  clean_val() / parse_beds()            MHTML: email.message_from_binary_file()
  batch 2000 rows / commit              normalize_hospital_name()
  idempotency key check                 SequenceMatcher >= 0.94 linking
       |                                          |
       v                                          v
[hospitals table: 29,974]         [insurer_hospital_records: 10]

[data/policies/*.pdf]               [data/claim_guidance/*.mhtml]
       |                                          |
       v                                          v
 ingest_policies.py                   ingest_claim_guidance.py
  pypdf -> PyMuPDF fallback            email.message_from_binary_file()
  header/footer removal                BeautifulSoup4 heading detection
  heading detection (UPPERCASE/regex)  accumulate until >= 800 chars
  sliding window 800-char             SHA-256 content hash
  1-line overlap carryover                         |
  SHA-256 content hash                             v
       |                              [documents: 5 + document_chunks: 24]
       v
[documents: 2 + document_chunks: 239]

All 263 document_chunks
       |
       +----------------------------+
       |                            |
       v                            v
sync_fts5_index()             index_all_chunks()
  DELETE FROM fts               for each chunk:
  INSERT FROM document_chunks     embed(title + heading + text)
  tokenize: porter unicode61      -> 128-dim L2-normalized vector
       |                          save to vector_index.json
       v                                    |
[document_chunks_fts: 263]                  v
                                 [vector_index.json: 263 x 128]
```

### 12.2 Query Answering Flow

```
POST /api/v1/qa/ask { question, document_type, max_citations }
       |
       v
  services/qa.py: answer_insurance_question()
       |
       +-- [1] Validate input (reject empty/whitespace)
       |
       +-- [2] services/retrieval.py: hybrid_search()
       |         |
       |         +-- BM25: search.py: search_document_chunks()
       |         |    normalize_query_words(query)
       |         |    FTS5 AND query (Tier 1)
       |         |    FTS5 OR query  (Tier 2 if < limit)
       |         |    -> List[Dict]: chunk_id, doc_title, excerpt, bm25_rank
       |         |
       |         +-- Vector: LocalVectorStore.search()
       |         |    embed_text(query) -> 128-dim vector
       |         |    np.dot(matrix_263x128, query_128) -> similarities
       |         |    filter by document_type if specified
       |         |    -> List[Dict]: chunk_id, similarity_score, vector_rank
       |         |
       |         +-- RRF Fusion:
       |              for each chunk: score = 0.5/(60+bm25+1) + 0.5/(60+vec+1)
       |              sort descending, deduplicate, return top_k
       |
       +-- [3] Relevance Filter
       |    keywords = extract_meaningful_keywords(q)
       |    required_matches = 2 if >=3 kw else 1
       |    retain chunks with keyword overlap >= threshold
       |
       +-- [4a] If citations exist:
       |    get_llm_provider() -> OllamaLLMProvider (default)
       |    POST http://localhost:11434/api/chat
       |    { model: "llama3.2", stream: false, temperature: 0.2,
       |      messages: [system_prompt, evidence_passages] }
       |    -> if LLM answer: generation_mode="RAG + LLM"
       |    -> if LLM unavailable: extractive fallback synthesis
       |
       +-- [4b] If no citations:
       |    status = "insufficient_evidence"
       |    is_sufficient_evidence = false
       |    citations = []
       |
       +-- [5] Append disclaimer + NETWORK_STATUS_CLARIFICATION if relevant
       |
       +-- [6] Persist to conversations + messages tables
       |
       v
  QuestionResponse JSON
```

### 12.3 Hospital Search & Network Status Flow

```
GET /api/v1/hospitals?search=kerudi&state=Karnataka
       |
       v
  api/v1/hospitals.py: get_hospitals()
       |
       +-- Normalize: isinstance checks on all params
       |
       +-- Route: source == "insurer"? -> query InsurerHospitalRecord
       |          else                 -> query Hospital (government dir)
       |
       +-- Government Directory path:
       |    SQL: SELECT * FROM hospitals
       |         WHERE hospital_name ILIKE "%kerudi%"
       |           OR address ILIKE "%kerudi%" ...
       |           AND state ILIKE "%Karnataka%"
       |    paginate: OFFSET (page-1)*page_size, LIMIT page_size
       |
       +-- Fetch ALL insurer_hospital_records (for status evaluation)
       |
       +-- For each result hospital:
       |    determine_hospital_network_status(h, all_insurer_records, total)
       |    -> "Not found in the imported network data"
       |       (Kerudi normalized name not in 10 insurer records,
       |        no FK link, no name match -> falls through to "Not found")
       |
       v
  HospitalListResponse {
    items: [{ hospital_name: "Kerudi Hospital And Research Centre",
              district: "Bagalkot", pincode: "587101",
              source_type: "Government Directory",
              network_status: "Not found in the imported network data" }],
    pagination: { page: 1, total_items: 1, ... }
  }
```

---

## 13. Evaluation Metrics & Results

### 13.1 Dataset Ingestion Metrics

| Metric | Value |
|---|---|
| Hospital directory rows read | 30,273 |
| Hospital records imported | 29,974 |
| Skipped hospital rows | 299 |
| Insurer network files | 2 |
| Insurer records imported | 10 |
| Insurer records linked to directory | 6 |
| Policy documents ingested | 2 |
| Policy chunks | 239 (179 full policy + 60 CIS) |
| Claim guidance documents | 5 |
| Claim guidance chunks | 24 |
| **Total document chunks** | **263** |
| FTS5 indexed passages | 263 |
| Vector embeddings | 263 |
| Vector index file size | 1,016,990 bytes |
| Vector dimension | 128 |

### 13.2 FTS5 Verified Search Queries

| Query | Results | Source |
|---|---|---|
| `cataract` | 3 | CIS (Physical Page 9) + Policy (Physical Pages 30, 32) |
| `waiting period` | 3 | Policy (Physical Pages 31, 41) + CIS (Physical Page 8) |
| `room rent` | 2 | Policy (Physical Page 9) |
| `pre-hospitalization` | 3 | Policy (Physical Pages 6, 11) + CIS (Physical Page 3) |
| `maternity` | 3 | Policy (Physical Pages 5, 34) + CIS (Physical Page 5) |
| `exclusions` | 3 | Policy (Physical Pages 31, 44) + CIS (Physical Page 18) |
| `cashless claims` | 3 | Cashless Guide + CIS (Physical Pages 14, 15) |
| `orbital space flight planetary excursion` | 0 | (correct abstention) |

### 13.3 QA System Evaluation (Live Verified)

| Question | Status | # Citations | Key Sources |
|---|---|---|---|
| Pre-existing disease waiting period | `answered` | 5 | Policy Physical Pages 41, 31; CIS Pages 4, 17 |
| Room-rent limits | `answered` | 3 | Policy Physical Page 9 (Printed 8/47) |
| Pre-hospitalization expenses | `answered` | 5 | Policy Physical Pages 11, 6; Claims Guide |
| Cataract treatment conditions | `answered` | 3 | CIS Physical Page 9; Policy Pages 30, 32 |
| Policy exclusions | `answered` | 3 | Policy Physical Pages 44, 31 |
| Orbital space flight | `insufficient_evidence` | 0 | (correct abstention) |
| How to bake sourdough bread | `insufficient_evidence` | 0 | (correct abstention) |

### 13.4 Hospital Network Status Tests (All Passed)

| Test Case | Expected Status | Result |
|---|---|---|
| Kerudi Hospital, Karnataka (no insurer match) | `"Not found in the imported network data"` | PASS |
| Baptist Hospital (FK-linked insurer record) | `"Listed in Star Health network data"` | PASS |
| Any hospital, empty insurer table | `"Network status not verified"` | PASS |
| Cambridge Hospital via insurer-network endpoint | `"Listed in Star Health network data"` | PASS |
| State mismatch (Karnataka vs Maharashtra) | `location_compatible() = False` | PASS |

### 13.5 Name Normalization Correctness

| Input A | Input B | Should Match? | Result |
|---|---|---|---|
| `"Apollo Hospitals - Bangalore"` | `"Apollo Hospital Bangalore"` | YES | PASS |
| `"BANGALORE BAPTIST HOSPITAL"` | `"Bangalore Baptist Hospital"` | YES | PASS |
| `"Kerudi Hospital & Research Centre"` | `"Kerudi Hospital And Research Centre"` | YES | PASS |
| `"St. John's Hospital"` | `"St Johns Hospital"` | YES | PASS |
| `"Chaitanya Hospital Pvt Ltd"` | `"Chaitanya Hospital"` | YES | PASS |
| `"Aditi Eye Care"` | `"Aditi Nursing Home"` | NO | PASS (different) |
| `"Manipal Northside Hospital"` | `"Manipal Hospital"` | NO | PASS (different) |
| `"Apollo Clinic"` | `"Apollo Hospitals"` | NO | PASS (different) |

### 13.6 Test Suite Results

| Suite | Tests | Passed | Status |
|---|---|---|---|
| `python -m pytest backend/tests` | 47 | 47 | All pass |
| `npm run build` (frontend) | 1,738 modules | 0 errors | Pass in 18.19s |

### 13.7 Abstention Performance

The system enforces strict abstention rather than hallucination. Verified:
- **False positive rate** on tested unsupported queries: **0%**
- `"orbital space flight"` -> 0 FTS5 hits, 0 vector hits -> abstention
- `"sourdough bread"` -> 0 hits -> abstention
- Abstention message always notes: "absence of a match does not prove exclusion"

---

## 14. Configuration Parameters

| Parameter | Default | Description |
|---|---|---|
| `APP_ENV` | `"development"` | `"testing"` disables auto-ingest |
| `DEBUG` | `True` | Show raw error messages |
| `DATABASE_URL` | `"sqlite:///./health_insurance.db"` | SQLAlchemy URL |
| `BACKEND_HOST` | `"127.0.0.1"` | Uvicorn bind host |
| `BACKEND_PORT` | `8000` | Uvicorn bind port |
| `CORS_ORIGINS` | `"http://localhost:5173,http://127.0.0.1:5173"` | Comma-separated allowed origins |
| `HOSPITALS_CSV_PATH` | `"data/hospitals/hospital_directory.csv"` | Government directory CSV |
| `INSURER_NETWORKS_DIR` | `"data/insurer_networks"` | Insurer HTML/MHTML directory |
| `EMBEDDING_PROVIDER` | `"local"` | `"local"` or `"sentence-transformers"` |
| `EMBEDDING_MODEL_NAME` | `"all-MiniLM-L6-v2"` | SentenceTransformers model (if used) |
| `VECTOR_STORE_PATH` | `"./vector_index.json"` | Dense vector index file path |
| `LLM_PROVIDER` | `"ollama"` | `"ollama"`, `"openai"`, `"gemini"`, `"auto"`, `"fallback"` |
| `LLM_MODEL_NAME` | `"gpt-4o-mini"` | OpenAI model name |
| `OLLAMA_MODEL_NAME` | `"llama3.2"` | Ollama model name |
| `OLLAMA_BASE_URL` | `"http://localhost:11434"` | Ollama API base URL |
| `OPENAI_API_KEY` | `""` | OpenAI API key (blank = disabled) |
| `GEMINI_API_KEY` | `""` | Gemini API key (blank = disabled) |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key (not yet wired) |
| `RAG_HYBRID_ALPHA` | `0.5` | BM25 weight in RRF (0.0 = vector-only, 1.0 = keyword-only) |
| `RAG_MAX_CITATIONS` | `5` | Default max citations per QA query |

---

## 15. Technology Stack & Dependencies

### Backend Python Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | >=0.110.0 | REST API framework |
| `uvicorn[standard]` | >=0.28.0 | ASGI server |
| `sqlalchemy` | >=2.0.28 | ORM + SQLite |
| `pydantic` | >=2.6.0 | Data validation |
| `pydantic-settings` | >=2.2.0 | .env configuration |
| `python-dotenv` | >=1.0.0 | .env file loading |
| `httpx` | >=0.27.0 | HTTP client for LLM calls |
| `numpy` | >=1.24.0 | Vector math |
| `beautifulsoup4` | >=4.12.0 | HTML/MHTML parsing |
| `pypdf` | >=4.0.0 | Primary PDF extraction |
| `PyMuPDF` | >=1.23.0 | Fallback PDF extraction |
| `aiosqlite` | >=0.20.0 | Async SQLite |
| `pytest` | >=8.0.0 | Test runner |
| `pytest-asyncio` | >=0.23.0 | Async tests |

### Frontend Dependencies

| Package | Purpose |
|---|---|
| React 18 + TypeScript | UI framework + type safety |
| Vite | Build tool + dev server |
| Tailwind CSS | Utility-first styling |
| lucide-react | Icon library |

### Infrastructure

| Component | Technology |
|---|---|
| Database | SQLite (file-based, no server required) |
| Full-text search | SQLite FTS5 (built-in, no external index) |
| Vector store | JSON flat file (custom LocalVectorStore class) |
| LLM inference | Ollama (local, CPU/GPU, no cloud required) |
| PDF extraction | pypdf (primary) + PyMuPDF (fallback) |
| HTML/MHTML parsing | BeautifulSoup4 + Python email module |
| Frontend bundler | Vite (1,738 modules, 18s build time) |

---

## 16. Limitations & Known Constraints

### Data Limitations

| Limitation | Detail |
|---|---|
| Insurer network coverage | Only 10 records from one offline Bangalore capture. Does not cover rest of India. |
| Hospital directory completeness | 29,974 records from NHA. May not include recently opened or private hospitals not in NHA registry. |
| Policy version | Indexed against `POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)` only. |
| Claims guidance currency | Web archives saved at a fixed point; Star Health may have updated procedures. |

### Technical Limitations

| Limitation | Detail |
|---|---|
| No live LLM by default | Requires Ollama with `llama3.2` locally, or API keys configured. Falls back to extractive synthesis. |
| Embedding quality | `LocalDenseEmbeddingProvider` uses polynomial hashing, not learned embeddings. Semantic recall lower than transformer models. |
| No query expansion | No synonym expansion or query rewriting. |
| No multi-hop reasoning | Single retrieval + single generation pass per question. |
| FTS5 language | Porter stemmer is English-optimized. Mixed-language hospital names not handled. |

### Safety Guarantees

| Guarantee | Implementation |
|---|---|
| No fabricated coverage claims | Relevance filter + abstention path; LLM system prompt forbids inventing clauses |
| Source attribution on every answer | All citations include document_title, version, page_number, section_heading, content_hash |
| Dataset separation | Government directory and insurer network in separate tables, never merged without disclosure |
| Absence != exclusion | Abstention messages explicitly state this |
| Network status disclaimer | Always shown when hospital/cashless/network/directory appears in QA query |

---

*All values, file paths, parameters, and metrics reflect the actual state of the codebase as of 2026-10-13.*
