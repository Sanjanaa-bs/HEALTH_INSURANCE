# AI-Assisted Health Insurance Information Platform

An evidence-grounded, full-stack intelligence platform engineered to assist policyholders, advisors, and evaluators in analyzing health insurance policies, understanding claims procedures, locating network hospitals, and receiving strictly cited, hallucination-free answers to policy inquiries.

---

## 📋 Table of Contents

- [1. Project Purpose & Objectives](#1-project-purpose--objectives)
- [2. System Features & Key Capabilities](#2-system-features--key-capabilities)
- [3. Technology Stack & Architecture](#3-technology-stack--architecture)
- [4. Project Directory Structure](#4-project-directory-structure)
- [5. Installation & Environment Setup](#5-installation--environment-setup)
- [6. Database Ingestion Pipeline](#6-database-ingestion-pipeline)
- [7. Startup Instructions](#7-startup-instructions)
- [8. API Endpoints Reference](#8-api-endpoints-reference)
- [9. Testing & Verification Commands](#9-testing--verification-commands)
- [10. Citation & Evidence Grounding Mechanics](#10-citation--evidence-grounding-mechanics)
- [11. Verified Policy Claims](#11-verified-policy-claims)
- [12. Hospital Directory vs. Network Limitations](#12-hospital-directory-vs-network-limitations)
- [13. Known Limitations & Roadmap](#13-known-limitations--roadmap)

---

## 1. Project Purpose & Objectives

Health insurance contracts in India are notoriously difficult for consumers to navigate. Documents like the **Star Comprehensive Insurance Policy** (48 pages) and its **Customer Information Sheet (CIS)** (20 pages) are packed with technical clauses, specific waiting periods, sub-limits, room-rent proportionate deductions, and standard exclusions. Furthermore, consumers frequently confuse public hospital directories with insurer-specific cashless networks.

**Core Objectives**:
1. **Eliminate Hallucinations**: Implement a deterministic, retrieval-grounded Q&A mechanism that extracts and cites verbatim policy clauses rather than synthesizing ungrounded advice.
2. **Exact Evidence Traceability**: Provide page-accurate citations distinguishing physical PDF page numbers from printed policy booklet page numbers.
3. **Safety Abstention**: Strictly abstain when evidence is insufficient, explicitly clarifying that the absence of a match is not proof of policy exclusion.
4. **Data Separation**: Clearly distinguish general national hospital directory listings (29,974 public facilities) from insurer cashless network facilities (10 verified records).
5. **Interactive Guidance**: Offer step-by-step claims workflows for cashless hospitalization, reimbursement, document upload, and status tracking.

---

## 2. System Features & Key Capabilities

- 🤖 **Grounded Policy Q&A (`PolicyQA.tsx`)**:
  - Natural language inquiry bar with pre-configured sample questions.
  - Document-type filtering (All, Policy Terms, CIS, Claims Guidance, IRDAI FAQs).
  - Deterministic extractive retrieval (`provider: "retrieval_grounded_guidance"`).
  - Collapsible citation cards showing document title, version, physical page, printed page, section heading, SHA-256 hash, and verbatim excerpt.
  - Prominent abstention warnings when questions fall outside indexed evidence.
- 🔍 **BM25 Policy Passage Search (`PolicySearch.tsx`)**:
  - Full-text search powered by SQLite FTS5 with Porter stemming and BM25 ranking.
  - Bold match highlighting (`<b>terms</b>`) across 263 indexed knowledge chunks.
  - Active document catalogue drawer displaying all 7 indexed documents and metadata.
- 🏥 **Hospital Network Explorer (`HospitalExplorer.tsx`)**:
  - **National Hospital Directory Tab**: Paginated directory of 29,974 government-registered healthcare facilities searchable by name and state.
  - **Star Health Network Tab**: 10 verified Star Health cashless network hospitals in Bangalore with foreign-key links to directory entries.
  - Prominent safety notices that general directory listing does not equal Star Health cashless network status.
- 📄 **Interactive Claims Guidance (`ClaimsGuidance.tsx`)**:
  - Structured procedural walkthroughs for Cashless Hospitalisation, Reimbursement, Document Upload, and Claim Status Tracking.
  - Deep links into Policy Search and Q&A with disclaimers that guidance is educational.
- 📊 **Architecture & Metrics Overview (`DashboardSummary.tsx`)**:
  - Live system metric cards (total facilities, network records, indexed documents, chunks, and healthcheck status).

---

## 3. Technology Stack & Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 Frontend (Vite)                       │
│  - TypeScript + Tailwind CSS + Lucide Icons                           │
│  - App.tsx, PolicyQA, PolicySearch, HospitalExplorer, ClaimsGuidance  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend (/api/v1)                       │
│  - Python 3.10+, Uvicorn, Pydantic v2 Settings & Schemas               │
│  - Routers: health, dashboard, hospitals, documents, qa                │
│  - Centralized Error Envelopes & CORS Middleware                       │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│     Search & Retrieval Engine        │ │   SQLAlchemy 2.0 ORM Engine   │
│ - SQLite FTS5 (porter unicode61)     │ │ - hospitals (29,974 rows)     │
│ - BM25 Ranking                       │ │ - insurer_hospital_records    │
│ - Query Normalization & Stemming     │ │ - documents (7 rows)          │
│ - Keyword Overlap Verification       │ │ - document_chunks (263 rows)  │
│ - Citation Page Derivation           │ │ - conversations & messages    │
└──────────────────┬───────────────────┘ └───────────────┬───────────────┘
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Persistent Database & Preserved Datasets                 │
│  - health_insurance.db (SQLite 3.38+ with PRAGMA foreign_keys=ON)      │
│  - Preserved Source Files in data/ (PDFs, MHTMLs, CSVs)                │
└────────────────────────────────────────────────────────────────────────┘
```

- **Frontend**: React 18.3, TypeScript 5.5, Vite 5.4, Tailwind CSS 3.4, Lucide React.
- **Backend**: Python 3.10+, FastAPI 0.110+, Uvicorn 0.28+, Pydantic v2, SQLAlchemy 2.0+.
- **Database**: SQLite 3.38+ with FTS5 virtual tables (`document_chunks_fts`) and enforced foreign keys (`PRAGMA foreign_keys=ON`).
- **Extraction Tools**: PyMuPDF (`fitz`), `pypdf`, `beautifulsoup4`.
- **Testing**: PyTest with in-memory SQLite fixtures (27 passing tests), Vite production build.

---

## 4. Project Directory Structure

```
health-insurance-ai/
├── data/                                # Preserved original source datasets
│   ├── hospitals/                       # National hospital directory CSV (30,275 rows)
│   ├── insurer_networks/                # Star Health network hospital HTML & MHTML
│   ├── policies/                        # Clean Full Policy PDF (48 pgs) & CIS PDF (20 pgs)
│   ├── claim_guidance/                  # Cashless/reimbursement claim guides & IRDAI FAQs
│   └── data_readiness_report.md         # Comprehensive data audit & readiness report
├── docs/                                # Project documentation
│   ├── ARCHITECTURE.md                  # Detailed system architecture document
│   └── CAPSTONE_DEMO_GUIDE.md           # 5–7 min presentation script & evaluator Q&A
├── backend/                             # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/                      # Versioned REST endpoints
│   │   │   ├── health.py                # GET /api/v1/health
│   │   │   ├── dashboard.py             # GET /api/v1/dashboard/summary
│   │   │   ├── hospitals.py             # GET /api/v1/hospitals (directory & network)
│   │   │   ├── documents.py             # GET /api/v1/documents (metadata & search)
│   │   │   ├── qa.py                    # POST /api/v1/qa/ask
│   │   │   └── router.py                # Master API v1 router
│   │   ├── models/                      # SQLAlchemy ORM models
│   │   │   ├── hospital.py              # Hospital & InsurerHospitalRecord
│   │   │   ├── document.py              # Document & DocumentChunk
│   │   │   ├── chat.py                  # Conversation & Message
│   │   │   └── evaluation.py            # EvaluationResult
│   │   ├── schemas/                     # Pydantic v2 request/response schemas
│   │   ├── services/                    # Business logic & grounded Q&A
│   │   │   └── qa.py                    # Extractive synthesis & keyword verification
│   │   ├── config.py                    # Settings & environment variables
│   │   ├── database.py                  # DB engine, sessionmaker & PRAGMA setup
│   │   ├── search.py                    # SQLite FTS5 search & BM25 ranking
│   │   └── main.py                      # FastAPI entrypoint, CORS, error handling
│   └── tests/                           # Pytest test suite (27 tests)
│       ├── test_dashboard.py            # Dashboard metrics tests
│       ├── test_database.py             # Model constraints & cascade tests
│       ├── test_endpoints.py            # API pagination & validation error tests
│       ├── test_health.py               # Healthcheck & root tests
│       ├── test_ingestion_and_search.py # CSV/MHTML extraction & search tests
│       └── test_qa_endpoint.py          # Grounded Q&A, abstention & citation tests
├── frontend/                            # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── api/                         # Typed fetch client (client.ts)
│   │   ├── components/                  # UI components
│   │   │   ├── App.tsx                  # Root app & tab router
│   │   │   ├── Header.tsx               # Header with health badge
│   │   │   ├── PolicyQA.tsx             # Grounded Q&A view
│   │   │   ├── PolicySearch.tsx         # Passage search view
│   │   │   ├── HospitalExplorer.tsx     # National directory vs network view
│   │   │   ├── ClaimsGuidance.tsx       # Procedural claims guides
│   │   │   └── DashboardSummary.tsx     # Overview metrics & specs
│   │   ├── types/                       # TypeScript interfaces (index.ts)
│   │   └── index.css                    # Tailwind CSS directives
│   ├── package.json
│   └── vite.config.ts
├── scripts/                             # ETL, ingestion & verification scripts
│   ├── ingest_all.py                    # Master ingestion pipeline runner
│   ├── ingest_hospitals.py              # Hospital directory CSV importer
│   ├── ingest_insurer_networks.py       # Star Health cashless network extractor
│   ├── ingest_policies.py               # Clean PDF policy & CIS extractor
│   ├── ingest_claim_guidance.py         # MHTML claim guidance extractor
│   ├── test_search.py                   # Direct CLI search tester
│   └── test_e2e_qa.py                   # Direct CLI Q&A tester
├── health_insurance.db                  # Persistent SQLite database
├── requirements.txt                     # Backend Python dependencies
├── .env.example                         # Environment template
└── README.md                            # Main project README
```

---

## 5. Installation & Environment Setup

### 5.1 System Prerequisites
- **Python**: 3.10 or newer (tested on Python 3.10.0)
- **Node.js**: 18.x or newer (npm 9+)

### 5.2 Repository Configuration
1. Clone the repository and navigate to the root directory:
   ```bash
   git clone <repository-url>
   cd health-insurance-ai
   ```
2. Copy the environment configuration template:
   ```bash
   cp .env.example .env
   ```
   The project defaults to a local Ollama model for grounded answer generation. Install [Ollama](https://ollama.com/download), start the Ollama service, and download the configured model (`ollama pull llama3.2`). When Ollama is unavailable, Q&A falls back to displaying retrieved evidence excerpts.

3. Install Python backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 6. Database Ingestion Pipeline

To populate `health_insurance.db` from preserved source files under `data/`:
```bash
python scripts/ingest_all.py
```

### Verified Ingestion Metrics:
- **Government Hospital Directory**: 29,974 valid records imported into `hospitals`.
- **Star Health Cashless Network**: 10 records imported into `insurer_hospital_records` (6 confidently linked to directory facilities; ambiguous name matches are left unlinked).
- **Customer Information Sheet (CIS)**: 20 pages extracted -> 60 retrievable chunks.
- **Full Policy Terms Wording**: 48 pages extracted -> 179 retrievable chunks.
- **Official Claims Guidance**: 4 MHTML guides -> 8 retrievable chunks.
- **IRDAI Regulations FAQ**: 1 MHTML guide -> 16 retrievable chunks.
- **Total Search Index (SQLite FTS5)**: Exactly **263 chunks** synchronized.
- **Idempotency**: Running `python scripts/ingest_all.py` repeatedly does not create duplicate chunks or corrupted tables.

---

## 7. Startup Instructions

### 7.1 Start the FastAPI Backend
From the project root:
```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

### 7.2 Start Ollama (for generated answers)
Install Ollama, then download and start the configured model:
```bash
ollama pull llama3.2
ollama serve
```
Set `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`, and `OLLAMA_MODEL_NAME=llama3.2` in `.env`. If Ollama is not running, the application returns a grounded excerpt-based answer instead.

### 7.3 Start the React Frontend
In a separate terminal window:
```bash
cd frontend
npm run dev
```
- Application UI: `http://localhost:5173`

---

## 8. API Endpoints Reference

All API routes are prefixed under `/api/v1` and return structured JSON responses.

| Method | Endpoint | Parameters / Body | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | None | Returns backend status, DB connection, and service timestamp |
| `GET` | `/api/v1/dashboard/summary` | None | Returns counts of hospitals, network records, documents, and chunks |
| `GET` | `/api/v1/hospitals` | `page` (int), `page_size` (int), `search` (str), `state` (str) | Returns paginated national hospital directory with metadata |
| `GET` | `/api/v1/hospitals/{id}` | Path: `id` (int) | Returns hospital details and any linked insurer network records |
| `GET` | `/api/v1/hospitals/insurer-network` | `page` (int), `page_size` (int), `search` (str), `city` (str) | Returns paginated sample Star Health network hospitals; search covers name, address, city, state, and pincode |
| `GET` | `/api/v1/documents` | None | Lists all indexed policy, CIS, and guidance documents |
| `GET` | `/api/v1/documents/{id}/chunks` | Path: `id` (int), `page` (int), `page_size` (int) | Returns raw chunks for a specific document |
| `GET` | `/api/v1/documents/search` | `q` (str, required), `document_type` (str), `limit` (int) | Performs SQLite FTS5 BM25 search across indexed chunks |
| `POST` | `/api/v1/qa/ask` | `{"question": str, "document_type": str, "max_citations": int}` | Submits question for grounded Q&A with exact citations |
| `POST` | `/api/v1/documents/ask` | `{"question": str, "document_type": str, "max_citations": int}` | Backward-compatibility alias for `/qa/ask` |

---

## 9. Testing & Verification Commands

### 9.1 Backend Automated Tests (Pytest)
Run the full 27-test suite:
```bash
python -m pytest backend/tests -v
```
*Current Result*: **27 passed out of 27 tests** in < 1.0s.

Test coverage breakdown:
- `test_health.py` (2 tests): Health check & root endpoints.
- `test_dashboard.py` (2 tests): Empty vs populated dashboard statistics.
- `test_database.py` (4 tests): ORM cascade deletion, unique constraints, and evaluation models.
- `test_endpoints.py` (3 tests): Hospital search pagination, document endpoints, and 422 error structures.
- `test_ingestion_and_search.py` (6 tests): CSV ingestion, MHTML parsing, FTS5 search, idempotency.
- `test_qa_endpoint.py` (10 tests): Grounded policy retrieval, version attribution, CIS vs Policy page calculation, clean abstention, empty query validation, network status warnings, conversation persistence.

### 9.2 Frontend Production Build
Validate TypeScript types and the production Vite bundle:
```bash
cd frontend
npm run build
```
*Current Result*: **0 TypeScript errors, built cleanly in ~2.0s**.

### 9.3 Command-Line Verification Scripts
Test FTS5 search directly against the database:
```bash
python scripts/test_search.py
```

Test end-to-end Q&A and safety abstention directly:
```bash
python scripts/test_e2e_qa.py
```

---

## 10. Citation & Evidence Grounding Mechanics

To ensure legal accuracy and eliminate hallucination, citations distinguish **physical PDF page numbers** from **printed policy page numbers**:

1. **Cover Page Offset**:
   - Both the Full Policy PDF (48 physical pages) and the CIS PDF (20 physical pages) feature an unnumbered cover sheet as Physical Page 1.
   - Printed numbering begins on Physical Page 2:
     - Full Policy: Physical Page 2 = `1 / 47`, Physical Page 48 = `47 / 47`. Formula: `printed = page_number - 1`.
     - CIS: Physical Page 2 = `1 / 19`, Physical Page 20 = `19 / 19`. Formula: `printed = page_number - 1`.
2. **Page Label Derivation** (`backend/app/search.py::format_page_label`):
   - Full Policy Chunk: `Physical Page 41 (Printed Page 40/47)`
   - CIS Chunk: `Physical Page 9 (Printed Page 8/19)`
3. **Citation Integrity Attributes**:
   Every returned citation includes:
   - `document_title`: Official document name.
   - `document_type`: `policy`, `cis`, `claim_guidance`, or `faq`.
   - `version`: Verified policy identifier, e.g. `POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)`.
   - `page_label`: Human-readable label matching the physical booklet.
   - `section_heading`: Extracted clause section heading.
   - `content_hash`: Cryptographic SHA-256 hash guaranteeing passage integrity.
   - `supporting_text`: Verbatim excerpt.

---

## 11. Verified Policy Claims

The platform guarantees that claims regarding benefits, exclusions, or waiting periods are backed by exact verified policy passages:

### 1. Pre-Existing Disease (PED) Waiting Period
- **Standard Clause**: Excluded until the expiry of **24 months of continuous coverage** without break after the date of inception of the first policy.
- **Supporting Sources**:
  - Full Policy: Physical Page 41 (Printed Page 40/47, Section 8 *Portability*).
  - Full Policy: Physical Page 31 (Printed Page 30/47, Section 1 *Exclusion Code Excl 01*).
- **Optional Buy-Back Cover (Section II.25)**:
  - On payment of additional premium, the policyholder can opt to reduce the waiting period from 36 months to **12 months** (available on first purchase only).
  - Supporting Source: Full Policy Physical Page 30 (Printed Page 29/47).

### 2. Room Rent Limits & Proportionate Deductions
- **Room Category**: Covered up to **Private Single A/C room** (boarding and nursing expenses).
- **Proportionate Deduction Clause**:
  - *"Note: Any hospitalization expenses arising under this Policy, which vary based on the room rent occupied by the Insured Person will be considered in proportion to the room rent limit / room category stated in the Policy or actuals whichever is less."*
- **Supporting Sources**:
  - Full Policy: Physical Page 9 (Printed Page 8/47, Section B.1 *Schedule against this In-Patient treatment*).
  - CIS: Physical Page 10 (Printed Page 9/19, Table 4).

### 3. Pre-Hospitalization Expenses
- **Coverage Period**: Medical expenses incurred for a period **not exceeding 60 days prior to the date of hospitalization** are payable, subject to an admissible hospitalization claim.
- **Post-Hospitalization Comparison**: Post-hospitalization expenses are payable for up to **90 days** from the date of discharge (Section B.6).
- **Supporting Sources**:
  - Full Policy: Physical Page 11 (Printed Page 10/47, Section B.5 *Pre-Hospitalization Expenses*).
  - Full Policy: Physical Page 6 (Printed Page 5/47, *Definitions*).

### 4. Cataract Treatment Terms
- **Waiting Period**: Listed under specific diseases/procedures subject to a **24-month waiting period** of continuous coverage.
- **Sub-Limits**: Treatments for cataract and anterior/posterior chamber of the eye are subject to specific sub-limits per eye based on the chosen sum insured.
- **Supporting Sources**:
  - CIS: Physical Page 9 (Printed Page 8/19, Section F.i).
  - Full Policy: Physical Page 30 (Printed Page 29/47) & Physical Page 32 (Printed Page 31/47, Section F.i).

---

## 12. Hospital Directory vs. Network Limitations

A critical distinction enforced throughout the user interface:

| Attribute | National Hospital Directory | Star Health Insurer Network |
| :--- | :--- | :--- |
| **Record Count** | 29,974 healthcare facilities | 10 sample facilities (Bangalore) |
| **Source** | Open Government Data Portal (`hospital_directory.csv`) | Extracted Star Health provider cards (HTML/MHTML) |
| **Network Status** | **NOT** an insurer network | Verified Star Health Cashless Network |
| **Cashless Guarantee** | No cashless facility implied | Pre-authorization required; no guarantee of approval |

> ⚠️ **Mandatory System Disclaimers**:
> 1. Inclusion of a facility in the National Hospital Directory does NOT establish Star Health network membership.
> 2. Network hospital listing does NOT guarantee cashless authorization or claim approval, which remains subject to policy terms and insurer pre-authorization.

---

## 13. Known Limitations & Roadmap

### Current Limitations
1. **Local Ollama Requirement**: Q&A uses Ollama when available. Without a running model, it returns retrieved evidence excerpts without generated paraphrasing.
2. **Sample Network Dataset**: The Star Health network contains 10 extracted sample records from Bangalore. A missing sample match does not mean that a hospital is outside the insurer's current network; this is not a comprehensive nationwide or live lookup.
3. **Bed Counts**: The included directory CSV has nonzero bed counts for 61 of 30,273 source rows. The UI displays counts when the source provides them and labels missing counts as unreported; network records may show a count only when safely linked to a directory record.
4. **No Transactional Claims API**: The platform provides educational claims guidance based on official documentation; it does not execute live claim submissions or query real-time claim status.
5. **Single Insurer Scope**: Grounded in Star Comprehensive Insurance Policy (UIN: `SHAHLIP26044V092526`).

### Future Roadmap
- 🌐 **Nationwide Provider Ingestion**: Automate scraping and batch ETL for insurer-wide network hospital directories.
- 📑 **OCR for Claim Invoices**: Add multi-modal OCR ingestion for hospital discharge summaries and medical bills.
- 🏥 **ABDM / FHIR Integration**: Connect to Ayushman Bharat Digital Mission (ABDM) APIs for real-time health insurance policy verification and digital health records.
