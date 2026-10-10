# Project Architecture Specification

**Project**: AI-Assisted Health Insurance Information Platform  
**Repository**: `health-insurance-ai`  
**Primary Stack**: React 18 (TypeScript, Vite, Tailwind CSS) + FastAPI (Python 3.10+, SQLAlchemy 2.0, SQLite FTS5)  
**Status**: Production Capstone Submission  

---

## 1. System Overview & High-Level Architecture

The Health Insurance Intelligence Platform is a full-stack, retrieval-grounded application engineered to provide transparent, strictly cited answers to health insurance inquiries, navigate policy wording, search claims procedures, and explore hospital networks.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 Frontend (Vite)                       │
│  ┌───────────────┐ ┌────────────────┐ ┌───────────────┐ ┌───────────┐  │
│  │   Policy QA   │ │ Policy Search  │ │   Hospitals   │ │  Claims   │  │
│  │  (Grounded)   │ │  (BM25 FTS5)   │ │ (Gov vs Net)  │ │ Guidance  │  │
│  └───────┬───────┘ └───────┬────────┘ └───────┬───────┘ └─────┬─────┘  │
└──────────┼─────────────────┼──────────────────┼───────────────┼────────┘
           │ HTTP POST       │ HTTP GET         │ HTTP GET      │ HTTP GET
           ▼                 ▼                  ▼               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend (/api/v1)                       │
│  ┌───────────────┐ ┌────────────────┐ ┌───────────────┐ ┌───────────┐  │
│  │   /qa/ask     │ │/documents/searc│ │  /hospitals   │ │/dashboard │  │
│  └───────┬───────┘ └───────┬────────┘ └───────┬───────┘ └───────────┘  │
│          │                 │                  │                        │
│          ▼                 ▼                  ▼                        │
│  ┌──────────────────────────────────┐ ┌─────────────────────────────┐  │
│  │    Search & Retrieval Engine     │ │   SQLAlchemy 2.0 ORM Engine │  │
│  │  - SQLite FTS5 BM25 Ranking      │ │  - Hospital & Network Tables│  │
│  │  - Keyword Extraction & Overlap  │ │  - Document & Chunk Tables  │  │
│  │  - Citation Page Derivation      │ │  - Conversations & Messages │  │
│  │  - Extractive Grounded Synthesis │ └──────────────┬──────────────┘  │
│  └──────────────────┬───────────────┘                │                 │
└─────────────────────┼────────────────────────────────┼─────────────────┘
                      │                                │
                      ▼                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  Persistent SQLite Database & Datasets                 │
│  - health_insurance.db (SQLite 3.38+ with FTS5 & Foreign Keys)          │
│  - 29,974 General Hospital Directory Records                           │
│  - 10 Verified Star Health Network Records                             │
│  - 263 Indexed Knowledge Chunks across 7 Documents                      │
│  - Source PDFs, MHTMLs, and CSVs preserved under data/                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Component Architecture

The frontend is built with React 18, TypeScript, Tailwind CSS, and Lucide icons, bundled using Vite. It enforces strict type safety via `frontend/src/types/index.ts`.

### 2.1 Navigation & Layout
- **`Header.tsx`**: Displays system status, live backend health indicator (`GET /api/v1/health`), database connection state, and manual refresh controls.
- **`App.tsx`**: Master orchestrator managing global state, cross-tab navigation (e.g., jumping from Claims Guidance to Policy QA or Search), active tab routing, and connection alert banners.

### 2.2 Primary Feature Modules
1. **`PolicyQA.tsx` (`Ask a Policy Question`)**:
   - Natural language input bar with sample question chips (PED waiting period, room rent, cataract, pre-hospitalization, exclusions, unsupported inquiry).
   - Document type filter dropdown (`All Documents`, `Full Policy Terms`, `Customer Information Sheet (CIS)`, `Official Claims Guidance`, `IRDAI FAQs`).
   - Loading skeletons during retrieval.
   - Grounded answer display with markdown formatting and copy-to-clipboard functionality.
   - Expandable/collapsible citation cards showing source document title, version, physical page, printed page, section heading, content hash, and exact supporting excerpt.
   - Clean abstention banners (`status: "insufficient_evidence"`) when indexed evidence is absent.
2. **`PolicySearch.tsx` (`Search Policy Documents`)**:
   - Direct SQLite FTS5 full-text search interface with BM25 ranking.
   - Filterable by document type with real-time excerpt highlighting (`<b>term</b>`).
   - Active document catalogue drawer showing all indexed policy and guidance files.
3. **`HospitalExplorer.tsx` (`Explore Hospitals`)**:
   - Tabbed interface enforcing strict source separation:
     - **National Hospital Directory**: 29,974 public facilities with state, district, ownership, and bed counts (`GET /api/v1/hospitals`).
     - **Star Health Network (Cashless)**: 10 verified network hospitals (`GET /api/v1/hospitals/insurer-network`).
   - Prominent disclaimer clarifying that inclusion in the national directory does not imply Star Health network membership, and network listing does not guarantee cashless authorization.
4. **`ClaimsGuidance.tsx` (`Claims Guidance`)**:
   - Interactive step-by-step guides for Cashless Hospitalisation, Reimbursement, Document Upload, and Claim Status Tracking.
   - Direct deep-links into Policy QA and Policy Search.
   - Clear disclosure that procedures are informational and do not guarantee claim settlement.
5. **`DashboardSummary.tsx` (`Overview & Architecture`)**:
   - Metric cards showing total facilities, network records, documents, retrievable chunks, and system health.
   - Technical specifications and data readiness summaries.
6. **`DocumentExplorer.tsx`**:
   - Dual-mode exploration component combining grounded Q&A and passage search.

---

## 3. FastAPI Backend Architecture

The backend is built with Python 3.10+ and FastAPI, adhering to asynchronous lifespan events, typed Pydantic v2 schemas, and centralized error envelopes.

### 3.1 Application Lifecycle & Configuration
- **`backend/app/config.py`**: Manages environment variables using `pydantic-settings`. Configures database URL, API prefix (`/api/v1`), debug flags, and CORS whitelist (`http://localhost:5173`, `http://127.0.0.1:5173`).
- **`backend/app/main.py`**:
  - Implements an asynchronous `lifespan` handler that initializes SQLite tables on startup via `init_db()`.
  - Configures CORS middleware for development origins.
  - Registers structured exception handlers for `StarletteHTTPException`, `RequestValidationError`, and generic `Exception`.

### 3.2 Error Envelope Contract
All HTTP responses adhere to a consistent error envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Question cannot be empty or whitespace only.",
    "details": null
  }
}
```

### 3.3 Registered API Endpoints (`/api/v1`)
| Method | Route | Router File | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | `health.py` | Healthcheck returning DB status, version, and timestamp |
| `GET` | `/api/v1/dashboard/summary` | `dashboard.py` | Aggregate statistics of hospitals, chunks, documents |
| `GET` | `/api/v1/hospitals` | `hospitals.py` | Paginated national hospital directory with search & state filter |
| `GET` | `/api/v1/hospitals/{id}` | `hospitals.py` | Single hospital detail with linked insurer records |
| `GET` | `/api/v1/hospitals/insurer-network` | `hospitals.py` | Paginated Star Health network hospitals |
| `GET` | `/api/v1/documents` | `documents.py` | Indexed documents with chunk counts and processing status |
| `GET` | `/api/v1/documents/{id}/chunks` | `documents.py` | Paginated raw chunks for a specific document |
| `GET` | `/api/v1/documents/search` | `documents.py` | BM25 full-text search across indexed chunks |
| `POST` | `/api/v1/qa/ask` | `qa.py` | Primary grounded question answering endpoint |
| `POST` | `/api/v1/documents/ask` | `documents.py` | Backward-compatibility alias for `/qa/ask` |

---

## 4. Database Schema & Ingestion Pipeline

### 4.1 Storage Engine
- **Engine**: SQLite 3.38+ with WAL journal mode.
- **Connection Configuration**: `backend/app/database.py` enforces foreign key constraints via `PRAGMA foreign_keys=ON;` on every connection.

### 4.2 ORM Data Models (`backend/app/models/`)
1. **`hospitals` (`Hospital`)**:
   - `id`, `name`, `state`, `district`, `city`, `pincode`, `address`, `hospital_type`, `total_beds`, `contact_number`, `latitude`, `longitude`, `created_at`.
2. **`insurer_hospital_records` (`InsurerHospitalRecord`)**:
   - `id`, `hospital_id` (Nullable Foreign Key to `hospitals.id`), `insurer_name`, `provider_hospital_name`, `city`, `state`, `pincode`, `address`, `network_status`, `raw_source_file`, `created_at`.
3. **`documents` (`Document`)**:
   - `id`, `title`, `document_type` (`policy`, `cis`, `claim_guidance`, `faq`), `source_file_path`, `version`, `is_processed`, `metadata_json`, `created_at`.
4. **`document_chunks` (`DocumentChunk`)**:
   - `id`, `document_id` (Foreign Key to `documents.id`), `chunk_index`, `text`, `page_number`, `section_heading`, `content_hash` (SHA-256), `created_at`.
   - Unique constraint: `(document_id, chunk_index)`.
5. **`conversations` (`Conversation`)**:
   - `id` (UUID), `title`, `created_at`, `updated_at`.
6. **`messages` (`Message`)**:
   - `id`, `conversation_id` (Foreign Key to `conversations.id`), `role` (`user`, `assistant`), `content`, `citations` (JSON text), `created_at`.
7. **`evaluation_results` (`EvaluationResult`)**:
   - `id`, `test_case_id`, `category`, `expected_behavior`, `passed`, `actual_output`, `metrics_json`, `created_at`.

### 4.3 Ingestion Pipeline Scripts (`scripts/`)
- **`scripts/ingest_hospitals.py`**:
  - Streams `data/hospitals/hospital_directory.csv` (10.3 MB).
  - Skips empty rows and header artifacts; imports **29,974 records**.
  - Idempotent: checks for existing records before insertion.
- **`scripts/ingest_insurer_networks.py`**:
  - Parses Star Health cashless network listings from HTML and MHTML sources.
  - Extracts 10 records, deduplicating identical hospital names.
  - Links 8 records to existing national directory entries via name/location matching.
- **`scripts/ingest_policies.py`**:
  - Extracts text from `data/policies/CIS_Star_Comprehensive_Insurance_Policy_V_2_69c15a9ee1.pdf` (20 physical pages, 60 chunks).
  - Extracts text from `data/policies/Policy_Star_Comprehensive_Insurance_Policy_clean.pdf` (48 physical pages, 179 chunks).
  - Normalizes whitespace, removes header/footer noise (`\d+ / 47`, company headers), preserves physical page numbers and headings.
  - Generates SHA-256 content hashes for tamper verification.
- **`scripts/ingest_claim_guidance.py`**:
  - Parses 4 Star Health claim guidance MHTML files (Cashless, Reimbursement, Document Upload, Claim Status) into 8 chunks.
  - Parses `data/claim_guidance/irdai_health_insurance_faqs.mhtml` into 16 chunks.
- **`scripts/ingest_all.py`**:
  - Master pipeline executing all ingestion modules sequentially and rebuilding the FTS5 search index.
  - Total records imported: **30,000 entities** (29,974 directory + 10 network + 7 documents + 263 chunks).

---

## 5. Search & Retrieval Flow

Search is handled by `backend/app/search.py` using SQLite Full-Text Search (FTS5):

```
User Query: "What expenses are covered before hospitalization?"
                         │
                         ▼
             [Query Normalization]
  - Phrase expansion: "before hospitalization" -> "pre hospitalization"
  - Spelling normalization: "hospitalisation" -> "hospitalization"
  - Stopword removal: ["what", "are", "covered", "is", "for", ...]
  - Resulting tokens: ["pre", "hospitalization", "expenses"]
                         │
                         ▼
             [SQLite FTS5 Query Match]
  - Tier 1: Strict AND query: '"pre" AND "hospitalization" AND "expenses"'
  - Tier 2: Fallback OR query: '"pre" OR "hospitalization" OR "expenses"'
            Ranked by SQLite BM25 score: bm25(document_chunks_fts)
                         │
                         ▼
          [Fallback Memory Search (if needed)]
  - If FTS5 is unindexed, runs in-memory tokenized scoring over document_chunks
                         │
                         ▼
            [Citation Page Derivation]
  - Maps physical PDF page to printed page number and page label
                         │
                         ▼
             Top Ranked Chunks Returned
```

### 5.1 FTS5 Configuration
- Table: `document_chunks_fts`
- Tokenizer: `porter unicode61` (handles Porter stemming and case folding).
- Indexed Columns: `text`, `section_heading`.
- Unindexed Metadata: `chunk_id`, `document_id`.

---

## 6. Question Answering & Grounded Synthesis Mechanism

The Q&A pipeline (`backend/app/services/qa.py`) implements a **deterministic extractive retrieval guidance model** (`provider: "retrieval_grounded_guidance"`):

### 6.1 Processing Steps
1. **Input Validation**: Strips whitespace; rejects empty inputs with HTTP 422.
2. **Passage Retrieval**: Fetches top relevant passages from `search_document_chunks` (up to `max_citations`, default 5).
3. **Keyword Overlap Verification**:
   - Extracts non-trivial domain tokens via `extract_meaningful_keywords`.
   - Requires multi-keyword overlap (at least 2 matching tokens for queries with 3+ keywords) against retrieved chunk text.
   - Prevents incidental common-word matches from triggering false answers.
4. **Structured Answer Synthesis**:
   - If overlap succeeds, groups passages by document type:
     - **Full Policy Wording**: Prefixed with `Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)`.
     - **Customer Information Sheet (CIS)**: Prefixed with `Star Comprehensive Customer Information Sheet (CIS, Version: V.2 / 2025)`.
     - **Claims Guidance**: Prefixed with `Star Health Official Claims Guidance`.
     - **IRDAI Regulations FAQ**: Prefixed with `IRDAI Health Insurance Regulations FAQ`.
   - Attaches page labels, section headings, and verbatim supporting excerpts.
5. **Hospital Network Clarification**:
   - If the query references "hospital", "network", "cashless", or "directory", automatically appends a mandatory clarification that directory listing does not equal Star Health network membership, and network listing does not guarantee cashless approval.
6. **Persistence**: Saves the user question and synthesized assistant response (with serialized citations JSON) into `conversations` and `messages` tables.

---

## 7. Citation Construction & Page Derivation

Accurate source citation is critical for insurance policy interpretation. Citations distinguish physical PDF page numbers from printed policy page numbers via `format_page_label()`:

| Document | Total Physical Pages | Cover Page Rule | Printed Page Formula | Example Citation |
| :--- | :--- | :--- | :--- | :--- |
| **Customer Information Sheet (CIS)** | 20 pages | Page 1 = Cover / Header | `printed = page_number - 1` | `Physical Page 9 (Printed Page 8/19)` |
| **Full Policy Terms & Conditions** | 48 pages | Page 1 = Cover Page | `printed = page_number - 1` | `Physical Page 41 (Printed Page 40/47)` |
| **MHTML Claims Guidance** | N/A (Web/MHTML) | No physical pages | N/A | `Document Title (Section Heading)` |

Every returned citation includes:
- `chunk_id`: Database primary key of the chunk.
- `document_id`: Database primary key of the parent document.
- `document_title`: Full official document name.
- `document_type`: `policy`, `cis`, `claim_guidance`, or `faq`.
- `version`: Official policy version and UIN.
- `page_number`: Physical PDF page (1-indexed).
- `printed_page_number`: Printed page number appearing on the physical document footer.
- `page_label`: Human-readable label (e.g. `Physical Page 11 (Printed Page 10/47)`).
- `section_heading`: Policy section header extracted from text.
- `supporting_text`: Verbatim passage excerpt.
- `content_hash`: SHA-256 integrity hash of chunk content.

---

## 8. Evidence Insufficiency & Abstention Behavior

When a question cannot be verified from indexed source chunks:
1. **Clean Abstention**: The service returns:
   - `status`: `"insufficient_evidence"`
   - `is_sufficient_evidence`: `false`
   - `citations`: `[]`
2. **Explicit Abstention Message**:
   > *"I cannot verify an answer to your question ('...') from the available policy documents or claims guidance. The system strictly abstains when verified evidence is absent to prevent inaccurate statements regarding insurance coverage, waiting periods, or exclusions. Note that the absence of a search match does not prove that a condition is excluded or not covered—please verify with official Star Health policy wording or your insurance provider."*
3. **Absence != Exclusion Principle**: Prevents the system from misinforming policyholders that an unmentioned procedure is excluded or denied.

---

## 9. Architectural Limitations & Boundaries

1. **Deterministic Retrieval vs Generative LLM**:
   - The platform uses deterministic extractive synthesis (`provider: "retrieval_grounded_guidance"`).
   - No external paid LLM API keys (OpenAI, Anthropic, Gemini) are configured. While this prevents hallucinations, responses are structured verbatim excerpts rather than free-form paraphrasing.
2. **Hospital Network Dataset Scale**:
   - The national hospital directory contains 29,974 records.
   - The Star Health network contains **10 verified records** extracted from available offline samples. It does not represent Star Health's complete nationwide network of thousands of hospitals.
3. **No Live Claims Execution**:
   - Claims guidance is strictly informational. The platform does not submit claims, process pre-authorizations, or query live claim status from Star Health servers.
4. **Static Policy Scope**:
   - Grounded specifically in Star Comprehensive Insurance Policy (UIN: `SHAHLIP26044V092526`, Version: `POL / COMP / V.24 / 2025`) and associated CIS/claims guides. It does not cover other Star Health products or other insurance providers.
