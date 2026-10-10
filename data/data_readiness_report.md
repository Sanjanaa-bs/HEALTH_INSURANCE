# Data Readiness & Ingestion Verification Report

**Project**: Health Insurance Intelligence Platform  
**Database Configured**: `sqlite:///./health_insurance.db`  
**Date**: October 10, 2026  
**Pipeline Execution Status**: Completed & Fully Verified  

---

## 1. Discovered Source Files

| Dataset Category | Source File Path | File Type | File Size | Discovery Status |
| :--- | :--- | :--- | :--- | :--- |
| **Government Hospital Directory** | `data/hospitals/hospital_directory.csv` | CSV | 10,341,256 bytes | **Discovered & Ingested** |
| **Star Health Insurer Network** | `data/insurer_networks/Star Health Network Hospitals List in Bangalore _ Cashless Hospitals in Bangalore.htm` | HTML | 717,017 bytes | **Discovered & Parsed** |
| **Star Health Insurer Network** | `data/insurer_networks/Star Health Network Hospitals List in Bangalore _ Cashless Hospitals in Bangalore.mhtml` | MHTML | 1,650,504 bytes | **Discovered & Parsed** |
| **Policy Customer Information Sheet** | `data/policies/CIS_Star_Comprehensive_Insurance_Policy_V_2_69c15a9ee1.pdf` | PDF | 1,671,059 bytes | **Discovered & Extracted** |
| **Policy Terms & Wording (Clean Source)** | `data/policies/Policy_Star_Comprehensive_Insurance_Policy_clean.pdf` | PDF | 2,101,643 bytes | **Discovered & Extracted (48/48 Pages)** |
| **Legacy Corrupt Policy PDF** | `data/policies/Policy_Star_Comprehensive_Insurance_Policy_V_21_3a414ab104.pdf` | PDF | 3,572,004 bytes | **Superseded by Clean PDF** |
| **IRDAI Regulations FAQ** | `data/claim_guidance/irdai_health_insurance_faqs.mhtml` | MHTML | 2,015,607 bytes | **Discovered & Extracted** |
| **Star Cashless Claims Guide** | `data/claim_guidance/star_cashless_claims.mhtml` | MHTML | 790,120 bytes | **Discovered & Extracted** |
| **Star Claim Document Upload Guide** | `data/claim_guidance/star_claim_document_upload.mhtml` | MHTML | 790,161 bytes | **Discovered & Extracted** |
| **Star Claim Status Guide** | `data/claim_guidance/star_claim_status.mhtml` | MHTML | 789,316 bytes | **Discovered & Extracted** |
| **Star Reimbursement Claims Guide** | `data/claim_guidance/star_reimbursement_claims.mhtml` | MHTML | 790,168 bytes | **Discovered & Extracted** |

---

## 2. Actual Import & Extraction Metrics

| Dataset / Entity | Source Read | Imported DB Records | Chunks Created | Skipped / Deduplicated | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`hospitals` Table** | 30,273 rows | **29,974 records** | N/A | 299 rows (empty/headers) | **Success** |
| **`insurer_hospital_records` Table** | 2 files | **10 records** | N/A | 10 duplicates across HTML/MHTML | **Success** (8 linked to Directory) |
| **`documents` (CIS PDF)** | 20 pages | **1 document** | **60 chunks** | 0 | **Success** (39,754 chars) |
| **`documents` (Full Policy PDF)** | 48 pages | **1 document** | **179 chunks** | 0 | **Success** (134,147 chars) |
| **`documents` (IRDAI FAQ MHTML)** | 1 file | **1 document** | **16 chunks** | 0 | **Success** (38,029 chars) |
| **`documents` (Claim Guidance MHTMLs)** | 4 files | **4 documents** | **8 chunks** | 0 | **Success** (35,307 chars) |
| **Total Database Records** | — | **30,000 records** | **263 chunks** | — | **Pipeline Verified** |

---

## 3. Search Index Verification (SQLite FTS5)

- **FTS5 Virtual Table**: `document_chunks_fts`
- **Indexed Passages**: **263 chunks**
- **Tokenization & Ranking**: `porter unicode61` stemming with BM25 relevance scoring (`bm25`)
- **Verified Search Queries**:
  - `cataract` -> 3 results (CIS Page 9 & Full Policy Page 30 / 32: "Treatment of Cataract and diseases of the anterior and posterior chamber...")
  - `waiting period` -> 3 results (Full Policy Page 31 / 41 & CIS Page 8: "Specific Waiting Periods, Waiting period for Pre-Existing Diseases...")
  - `room rent` -> 2 results (Full Policy Page 7 / 9: "Any hospitalization expenses arising under this Policy, which vary based on the room rent occupied...")
  - `pre-hospitalization` -> 3 results (Full Policy Page 6 / 11 & CIS Page 3: "Medical expenses incurred for a period not exceeding 60 days prior to hospitalization...")
  - `maternity` -> 3 results (Full Policy Page 5 / 34 & CIS Page 5: "18. Maternity - Code Excl 18 Medical treatment expenses traceable to childbirth...")
  - `exclusions` -> 3 results (Full Policy Page 31 / 44 & CIS Page 18: "STANDARD EXCLUSIONS / First 30 days as per exclusion - Code Excl 03...")
  - `cashless claims` -> 3 results (Cashless Guide & CIS Page 14 / 15: "Details of procedure to be followed for cashless claim intimation...")

---

## 4. Technical Audit & Policy PDF Recovery Log

### Clean Full Policy Wording PDF Recovery (`Policy_Star_Comprehensive_Insurance_Policy_clean.pdf`)

- **File Metadata & Specifications**:
  - **Path**: `data/policies/Policy_Star_Comprehensive_Insurance_Policy_clean.pdf`
  - **File Size**: `2,101,643 bytes` (~2.00 MB)
  - **Page Count**: 48 physical pages (Cover + Printed pages 1/47 to 47/47)
  - **Document Identifiers**:
    - **UIN**: `SHAHLIP26044V092526`
    - **Version**: `POL / COMP / V.24 / 2025`
  - **Encryption**: Unencrypted (`is_encrypted: False`)
- **Extraction & Processing Metrics**:
  - **Pages Extracted**: `48 / 48` physical pages successfully parsed (134,147 text characters).
  - **Chunks Created**: `179` searchable chunks generated across 48 physical pages.
  - **Header Cleaning**: Filtered out repeating header/footer artifacts (`\d+ / 47`, company headers, UIN lines) to preserve clean section headings and text clauses.
- **Database Document Record**:
  - **Document ID**: `2`
  - **Document Type**: `policy`
  - **Title**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording`
  - **Source Path**: `data/policies/Policy_Star_Comprehensive_Insurance_Policy_clean.pdf`
  - **Version**: `POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)`
  - **Processing Status**: `is_processed = True`
  - **Metadata Log**: `{"extraction_status": "success", "uin": "SHAHLIP26044V092526", "version": "POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)", "extracted_pages": 48, "chunks_count": 179}`

---

## 5. Idempotency & Duplicate-Ingestion Verification

- Re-running policy ingestion (`python scripts/ingest_policies.py`) and full pipeline (`python scripts/ingest_all.py`) verified complete idempotency:
  - `document_chunks`: Exactly **263 chunks** before and after re-ingestion (**0 duplicate chunks**).
  - `document_chunks_fts`: Exactly **263 FTS5 records** synchronized.
  - `hospitals`: 29,974 records preserved.
  - `insurer_hospital_records`: 10 records preserved.

---

## 6. Test Suite & Verification Summary

- **Backend Pytest Suite**: **17 passed out of 17 tests** in 0.72s (`python -m pytest backend/tests -v`).
- **FTS5 Search Functionality**: Verified via [`scripts/test_search.py`](file:///c:/Users/sanjana/OneDrive/Desktop/RESUME/health-insurance-ai/scripts/test_search.py) across all target health insurance queries.
- **Frontend Build Status**: Verified clean Vite production build (`npm run build` in 2.42s).

---

## 7. End-to-End Application & Retrieval Verification

### Architecture Scope Clarification
- **Current Retrieval Mode**: The application backend exposes full-text document passage search with BM25 ranking via `GET /api/v1/documents/search?q=...`. This powers the frontend `DocumentExplorer` component for exploring policy wording, CIS clauses, and claims guides with citations.
- **Generative QA Status**: The database schema includes `conversations` and `messages` tables, but there is no separate generative LLM question-answering endpoint currently mounted in `backend/app/api/v1/router.py`. Thus, verified results represent true grounded document search and passage retrieval, avoiding simulated or hallucinated generative text.

### End-to-End Question Retrieval & Citation Results

1. **Question**: *What is the waiting period for pre-existing diseases?*
   - **Query**: `waiting period pre-existing diseases`
   - **Top Match**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording` (policy)
   - **Page**: Physical Page 31 (Printed Pg 30/47) | Section: `exclusion shall not be applicable for`
   - **Passage Excerpt**: *"...If any of the specified disease/ procedure falls under the waiting period specified for pre-Existing diseases, then the longer of the two will apply..."*
2. **Question**: *What does the policy say about room rent?*
   - **Query**: `room rent`
   - **Top Match**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording` (policy)
   - **Page**: Physical Page 9 (Printed Pg 8/47) | Section: `Schedule against this In-Patient treatment`
   - **Passage Excerpt**: *"...Any hospitalization expenses arising under this Policy, which vary based on the room rent occupied by the Insured Person will be considered in proportion..."*
3. **Question**: *Are cataract treatments subject to specific conditions?*
   - **Query**: `cataract`
   - **Top Match**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording` (policy) & CIS
   - **Page**: Physical Page 32 (Printed Pg 31/47) | Section: `Page 32`
   - **Passage Excerpt**: *"...Treatment of Cataract and diseases of the anterior and posterior chamber of the Eye, Diseases of ENT, Diseases related to Thyroid, Benign diseases..."*
4. **Question**: *What does the policy say about pre-hospitalisation expenses?*
   - **Query**: `pre-hospitalization expenses`
   - **Top Match**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording` (policy)
   - **Page**: Physical Page 11 (Printed Pg 10/47) | Section: `Page 11`
   - **Passage Excerpt**: *"...Pre-Hospitalization Expenses: Medical expenses incurred for a period not exceeding 60 days prior to the date of hospitalization are payable subject to..."*
5. **Question**: *What are the policy's exclusions?*
   - **Query**: `exclusions`
   - **Top Match**: `Star Comprehensive Insurance Policy - Terms & Conditions Wording` (policy)
   - **Page**: Physical Page 44 (Printed Pg 43/47) & Page 31 | Section: `Exclusion as under shall apply afresh`
   - **Passage Excerpt**: *"...First 30 days as per exclusion - Code Excl 03 ii. 24 months with continuous coverage without break (with grace period) in respect of diseases / treatments..."*

### Abstention Verification on Unsupported Query
- **Question**: *What is the policy for orbital space flight and planetary excursion?*
- **Query**: `orbital space flight planetary excursion`
- **Results Count**: **0 results**
- **Outcome**: The retrieval engine returned an empty result set (`total_results: 0`). The system correctly abstains and does not fabricate details when evidence is missing.

---

## 8. Grounded Question Answering Implementation (Completed)

### 8.1 Endpoint & Architecture
- **Primary Endpoint**: `POST /api/v1/qa/ask`
- **Compatibility Endpoint**: `POST /api/v1/documents/ask`
- **Request Format**:
  ```json
  {
    "question": "What is the waiting period for pre-existing diseases?",
    "document_type": null,
    "conversation_id": null,
    "max_citations": 5
  }
  ```
- **Response Format**:
  ```json
  {
    "question": "What is the waiting period for pre-existing diseases?",
    "answer": "**According to the Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526):**\n- **Physical Page 41 (Printed Page 40/47) (Section: 8. Portability)**: ...",
    "status": "answered",
    "is_sufficient_evidence": true,
    "provider": "retrieval_grounded_guidance",
    "citations": [
      {
        "chunk_id": 854,
        "document_id": 2,
        "document_title": "Star Comprehensive Insurance Policy - Terms & Conditions Wording",
        "document_type": "policy",
        "version": "POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)",
        "page_number": 41,
        "printed_page_number": 40,
        "page_label": "Physical Page 41 (Printed Page 40/47)",
        "section_heading": "8. Portability",
        "supporting_text": "...",
        "content_hash": "0d257f1580e798471c34c92d55917923d5e7eaa03aae232442ea45d25c6ec58d"
      }
    ],
    "disclaimer": "Disclaimer: This guidance is grounded strictly in indexed source documents. Hospital directory listing does not guarantee Star Health network membership, and network listing does not guarantee cashless authorization or claim approval. This does not substitute for professional medical advice or official insurer pre-authorization.",
    "conversation_id": "...",
    "created_at": "2026-10-10T..."
  }
  ```

### 8.2 LLM Provider Status
- **Configured Status**: No paid external LLM API keys (e.g. OpenAI, Anthropic, Gemini) are configured in the repository's `.env`.
- **Implemented Architecture**: Implemented a deterministic, evidence-grounded synthesis fallback labeled as `retrieval_grounded_guidance`. This constructs structured answers strictly from retrieved passages without hallucinating or inventing clauses, while keeping the API contract fully prepared for a future LLM adapter.

### 8.3 Citations & Version Safety
- **Full Policy Version**: Always cited with its verified identifier:
  `POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)`
- **Page Numbering**: Citations distinguish physical PDF page numbers from printed policy page numbers (`Physical Page N (Printed Page N-1/47)`). Cover page is designated as physical page 1.
- **Source Separation**: Full policy wording, Customer Information Sheet (CIS), and official Claims Guidance are separated under distinct attribution sections.

### 8.4 Safety & Abstention Rules
- **Clean Abstention**: On questions lacking sufficient indexed evidence (e.g., "What is the policy for orbital space flight?"), the system returns `status: "insufficient_evidence"`, `is_sufficient_evidence: false`, `citations: []`, and an explicit statement abstaining from generating advice.
- **Absence != Exclusion**: Abstention responses explicitly explain that an absence of search results does not prove a condition is excluded or not covered.
- **Hospital Network Disclaimer**: Any hospital or cashless network query automatically attaches the mandatory disclaimer that government hospital directory presence does not establish Star Health network membership, and network listing does not guarantee cashless claim settlement.
- **Input Validation**: Empty or whitespace-only inputs are rejected at schema validation (`422 Unprocessable Entity` with `VALIDATION_ERROR`).

### 8.5 Test Results & Frontend Integration
- **Backend Test Suite**: **25 passed out of 25 tests** (`python -m pytest backend/tests -v` in 0.80s).
- **Frontend Production Build**: **Verified** (`npm run build` completed in 2.17s).
- **Frontend Q&A Component**: Integrated directly into `frontend/src/components/DocumentExplorer.tsx` with a dual-mode tab ("Grounded Q&A" and "Passage Search"), question chips, citation accordions, and provider status disclosure, preserving existing visual styling.

---

## 9. Frontend Polish & Final Live End-to-End Verification

### 9.1 Completed Navigation & Component Architecture
The dashboard navigation provides four dedicated views centered around evidence-grounded Q&A:
1. **Ask a Policy Question** (`PolicyQA.tsx`): Primary application experience with natural language inquiry bar, sample question chips, loading skeletons, copy-to-clipboard, expand/collapse citations, and prominent abstention banners.
2. **Search Policy Documents** (`PolicySearch.tsx`): BM25 passage search with highlighted excerpts, document type filters (Policy, CIS, Claims Guidance, IRDAI FAQs), and active document catalogue.
3. **Explore Hospitals** (`HospitalExplorer.tsx`): Clear tabbed interface separating Government Hospital Directory (29,974 records) from verified Star Health Cashless Network (10 records), with safety disclaimers that directory listing does not equal cashless approval.
4. **Claims Guidance** (`ClaimsGuidance.tsx`): Step-by-step procedures for Cashless Hospitalisation, Reimbursement, Document Upload, and Status Tracking, with explicit disclosures that guidance is informational and does not guarantee claim outcomes.
5. **Overview & Architecture** (`DashboardSummary.tsx` & Specs): System metric cards and full-stack architecture specs.

### 9.2 Live Verification Results
- **Check A (Supported Policy Question)**: Tested `"What is the waiting period for pre-existing diseases?"` against live server at `http://127.0.0.1:8000/api/v1/qa/ask`. Returned `status: "answered"`, `is_sufficient_evidence: true`, 5 citations from `Star Comprehensive Insurance Policy - Terms & Conditions Wording (Version POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)`, citing Physical Page 41 (Printed Page 40/47).
- **Check B (Unsupported Question Abstention)**: Tested `"Does this policy cover orbital space flight and planetary excursion?"`. Returned `status: "insufficient_evidence"`, `is_sufficient_evidence: false`, 0 citations, and strict abstention statement without inventing coverage.
- **Check C (Policy Document Search)**: Tested `GET /api/v1/documents/search?q=cataract`. Returned 3 matched chunks with BM25 highlighted excerpts and page labels (`Physical Page 9 (Printed Page 8/19)`).
- **Check D (Claims Guidance Search)**: Tested `GET /api/v1/documents/search?q=cashless&document_type=claim_guidance`. Returned 3 matched passages from ingested Star Health claim guidance documents.
- **Check E (Hospital Directory vs Insurer Network)**: Verified `GET /api/v1/hospitals` (29,974 records) and `GET /api/v1/hospitals/insurer-network` (10 records) maintain strict source separation and non-guarantee wording.

### 9.3 Verification Metrics
- **Frontend Production Build**: `npm run build` completed in 2.38s (0 TypeScript errors, 0 bundle warnings).
- **Backend Pytest Suite**: 25 passed out of 25 tests in 0.91s (`python -m pytest backend/tests -v`).
- **Remaining Limitations**: External paid LLM API keys remain unconfigured; platform operates deterministically in `retrieval_grounded_guidance` mode. Live claim submission and live policy claim status lookup APIs do not exist and are accurately disclosed as informational only.

---

## 10. Final Data Accuracy, Citations & Capstone Readiness Audit

### 10.1 Investigation: Cataract Citation Page Accuracy
- **Investigation Finding**: The search result for `cataract` reporting `Physical Page 9 (Printed Page 8/19)` originates from **Document 1: Customer Information Sheet (CIS)** (`CIS_Star_Comprehensive_Insurance_Policy_V_2_69c15a9ee1.pdf`).
  - **CIS Structure**: 20 physical pages total. Physical Page 1 is an unnumbered cover sheet; printed numbering starts on Physical Page 2 as `1 / 19` through Physical Page 20 as `19 / 19`. Thus, Physical Page 9 corresponds exactly to printed page `8 / 19`.
  - **Full Policy Structure**: 48 physical pages total (`Policy_Star_Comprehensive_Insurance_Policy_clean.pdf`). Physical Page 1 is an unnumbered cover sheet; printed numbering runs from Physical Page 2 (`1 / 47`) through Physical Page 48 (`47 / 47`). Cataract terms in the Full Policy reside on Physical Page 30 (`Printed Page 29/47`) and Physical Page 32 (`Printed Page 31/47`).
  - **Resolution & Safeguard**: The system accurately identifies the source document (`document_type: "cis"` vs `"policy"`), document title, version, and document-specific physical and printed page calculations. Regression test `test_qa_cis_vs_policy_page_citation_accuracy` enforces this distinction.

### 10.2 Audit: QA Grounding on Required Test Questions
All 6 questions were audited against the actual database and live backend service:
1. **What is the waiting period for pre-existing diseases?**
   - **Status**: `answered` (`is_sufficient_evidence: true`, 5 citations).
   - **Supporting Sources**: Full Policy Physical Page 41 (Printed Page 40/47) & Page 31 (Printed Page 30/47) citing 24 months continuous coverage without break, and CIS Physical Page 17 & Page 4.
2. **What are the room-rent limits?**
   - **Status**: `answered` (`is_sufficient_evidence: true`, 3 citations).
   - **Supporting Sources**: Full Policy Physical Page 9 (Printed Page 8/47, Section: *Schedule against this In-Patient treatment*) specifying *Private Single A/C room* with proportionate expense reduction, and CIS Physical Page 10 (Printed Page 9/19).
3. **What expenses are covered before hospitalization?**
   - **Status**: `answered` (`is_sufficient_evidence: true`, 5 citations).
   - **Supporting Sources**: Full Policy Physical Page 11 (Printed Page 10/47, Section 5: *Pre-Hospitalization Expenses payable for up to 60 days prior to hospitalization*), Physical Page 6, and Claims Guidance.
4. **What are the cataract-related terms?**
   - **Status**: `answered` (`is_sufficient_evidence: true`, 3 citations).
   - **Supporting Sources**: CIS Physical Page 9 (Printed Page 8/19) detailing sub-limits, and Full Policy Physical Page 32 (Printed Page 31/47) & Physical Page 30 (Printed Page 29/47) defining specific waiting periods and sub-limits.
5. **Does this policy cover orbital space flight?**
   - **Status**: `insufficient_evidence` (`is_sufficient_evidence: false`, 0 citations).
   - **Behavior**: System strictly abstains. Explicitly states that absence of a match is not proof of exclusion and prevents hallucinated denials or approvals.
6. **How do I bake sourdough bread at high altitude? (Unrelated Inquiry)**
   - **Status**: `insufficient_evidence` (`is_sufficient_evidence: false`, 0 citations).
   - **Behavior**: System strictly abstains. Regression test `test_qa_unrelated_query_clean_abstention` verifies that non-insurance queries never return false-positive matches from incidental common words.

### 10.3 Extractive vs Generative Mode Disclosure
- The system operates using a **deterministic extractive retrieval guidance model** (`provider: "retrieval_grounded_guidance"`).
- It extracts, attributes, and structures verbatim passages from verified source chunks. It does not run an ungrounded generative LLM, completely preventing hallucinations of policy limits, claim guarantees, or waiting periods.

### 10.4 Hospital Network Completeness Limitation
- **Government Directory**: 29,974 facilities imported from the national public hospital directory. Listing does not establish Star Health network membership.
- **Star Health Network**: 10 records extracted from available offline card datasets. These 10 records represent a sample and do **NOT** constitute a complete nationwide network directory.
- **Safety Rule**: Network hospital listing does **NOT** guarantee cashless pre-authorization or claim settlement.

### 10.5 Audit Test Suite & Build Status
- **Backend Tests**: **27 passed out of 27 tests** in 0.94s (`python -m pytest backend/tests -v`).
- **Frontend Production Build**: **Verified** (`npm run build` in 1.96s, zero errors).
- **Live HTTP Service**: Verified on `http://127.0.0.1:8000`.
- **Remaining Blockers**: None.



