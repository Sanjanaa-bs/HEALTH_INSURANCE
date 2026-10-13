# Capstone Project Demonstration & Presentation Guide

**Project**: AI-Assisted Health Insurance Information Platform  
**Target Audience**: Academic Evaluators, Capstone Review Panels, and Technical Assessors  
**Recommended Duration**: 5–7 Minutes  
**Demonstration URL**: `http://localhost:5173` (Frontend) | `http://127.0.0.1:8000/docs` (FastAPI Swagger)  

---

## 1. Environment Verification & Startup Instructions

Before presenting to evaluators, verify both services are running and healthy.

### 1.1 Backend Startup
Open a terminal in the project root:
```bash
# 1. Activate virtual environment (if applicable) and verify dependencies
pip install -r requirements.txt

# 2. (Optional) Run dataset ingestion if database is not initialized
python scripts/ingest_all.py

# 3. Start FastAPI server via Uvicorn
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- Verify: Open `http://127.0.0.1:8000/api/v1/health` in your browser. Expected: `{"status": "healthy", "database": "connected", ...}`.

### 1.2 Frontend Startup
Open a second terminal in `frontend/`:
```bash
cd frontend
npm install
npm run dev
```
- Verify: Access `http://localhost:5173`. The header should display **"Backend: Connected (v1.0.0)"** with a green badge.

### 1.3 Quick Automated Verification
Run the backend test suite before your demo to confirm all 27 tests pass:
```bash
python -m pytest backend/tests -v
```

---

## 2. 5–7 Minute Live Demonstration Script

| Timing | Segment | Screen / View | Action & Presenter Talking Points |
| :--- | :--- | :--- | :--- |
| **0:00 – 1:00** | **Introduction & Problem Statement** | Header & Overview Tab | *"Health insurance policies are dense legal contracts riddled with exclusions, sub-limits, and waiting periods. Policyholders struggle to verify coverage and distinguish general public hospitals from insurer cashless networks. Today, I am demonstrating an AI-assisted platform that provides deterministic, retrieval-grounded policy answers, exact source citations down to the printed page, and clear hospital network exploration."* |
| **1:00 – 2:30** | **Grounded Policy Q&A & Citation Integrity** | Ask a Policy Question (`PolicyQA.tsx`) | Click the sample chip: **"What is the waiting period for pre-existing diseases?"**.<br><br>*"Notice three key architectural choices: First, the answer synthesizes exact clauses from the Star Comprehensive Insurance Policy (Version POL / COMP / V.24 / 2025). Second, look at the citations below: Physical Page 41 clearly maps to Printed Page 40/47 in the policy, citing the 24-month continuous coverage rule and the optional 12-month buy-back clause. Third, notice the cryptographic SHA-256 content hash on each citation ensuring evidence provenance."* |
| **2:30 – 3:30** | **Safety Abstention & Hallucination Prevention** | Ask a Policy Question (`PolicyQA.tsx`) | Click the sample chip: **"Does this policy cover orbital space flight and planetary excursions?"**.<br><br>*"In health insurance, fabricating an answer can lead to denied medical claims. When evidence is missing, the system strictly abstains with an explicit warning banner: `I cannot verify an answer to your question... The system strictly abstains when verified evidence is absent.` Most importantly, it reminds the user that absence of a search match does not prove a condition is excluded."* |
| **3:30 – 4:30** | **Policy Passage Search & Document Disambiguation** | Search Policy Documents (`PolicySearch.tsx`) | Search for **"cataract"**.<br><br>*"In the Search tab, we query our SQLite FTS5 BM25 index over 263 chunks. Notice result #1 comes from the Customer Information Sheet (CIS) citing Physical Page 9 (Printed Page 8/19), while results #2 and #3 come from the Full Policy Wording citing Physical Page 30 and 32 (Printed Page 31/47). The system never confuses the 20-page CIS with the 48-page Full Policy."* |
| **4:30 – 5:30** | **Hospital Explorer & Data Integrity** | Explore Hospitals (`HospitalExplorer.tsx`) | Toggle between **Government Directory** and **Star Health Network** tabs.<br><br>*"Our database contains 29,974 facilities from the national hospital directory. However, we maintain strict source separation: listing in the national directory does NOT imply Star Health network membership. In the second tab, we showcase 10 verified Star Health network records. A prominent safety banner clarifies that network listing does not guarantee cashless pre-authorization, which requires insurer approval."* |
| **5:30 – 6:30** | **Claims Guidance Workflows** | Claims Guidance (`ClaimsGuidance.tsx`) | Open **Cashless Hospitalisation** and **Reimbursement** workflows.<br><br>*"Here policyholders receive step-by-step guidance on planned vs emergency cashless intimations and document submission checklists, cross-linked directly into our policy search and Q&A engine."* |
| **6:30 – 7:00** | **Conclusion & Architecture Summary** | Overview Tab (`DashboardSummary.tsx`) | *"To summarize: 27/27 automated tests passing, 30,000 entities indexed, zero hallucinated policy clauses, and full citation traceability from UI to source PDF."* Open floor for questions. |

---

## 3. Six Example Test Questions & Expected Behavior

Use these six benchmark questions during the demonstration to showcase accuracy, citation precision, and safety abstention.

### Test 1: Pre-Existing Disease Waiting Period (Supported)
- **Question**: `"What is the waiting period for pre-existing diseases?"`
- **Expected Status**: `answered` (`is_sufficient_evidence: true`, 5 citations)
- **Verified Policy Clauses**:
  - Full Policy Physical Page 41 (Printed Page 40/47, Section 8 Portability): 24 months continuous coverage without break.
  - Full Policy Physical Page 31 (Printed Page 30/47, Exclusion Code Excl 01): 24 months exclusion after policy inception.
  - Full Policy Physical Page 30 (Printed Page 29/47, Section II.25): Optional Cover Buy-Back allows reduction from standard 36 months to 12 months for first purchase on payment of additional premium.
  - CIS Physical Page 10 (Printed Page 9/19) & Page 17 (Printed Page 16/19).
- **Citations Displayed**: Full Policy Terms (Pages 30, 31, 41) and CIS (Pages 4, 17).

### Test 2: Room Rent Limits (Supported)
- **Question**: `"What does the policy say about room rent?"`
- **Expected Status**: `answered` (`is_sufficient_evidence: true`, 3 citations)
- **Verified Policy Clauses**:
  - Full Policy Physical Page 9 (Printed Page 8/47, Section B.1 Schedule against this In-Patient treatment): Covered up to *Private Single A/C room* (or Single Standard A/C Room depending on sum insured).
  - *Proportionate Deduction Note*: *"Any hospitalization expenses arising under this Policy, which vary based on the room rent occupied by the Insured Person will be considered in proportion to the room rent limit / room category stated in the Policy or actuals whichever is less."*
  - CIS Physical Page 10 (Printed Page 9/19, Table 4): Private Single A/C room.
- **Citations Displayed**: Full Policy Physical Page 9 (Printed Page 8/47), Physical Page 7, and CIS Physical Page 10.

### Test 3: Pre-Hospitalization Expenses (Supported)
- **Question**: `"What does the policy say about pre-hospitalisation expenses?"`
- **Expected Status**: `answered` (`is_sufficient_evidence: true`, 5 citations)
- **Verified Policy Clauses**:
  - Full Policy Physical Page 11 (Printed Page 10/47, Section B.5): *"Medical expenses incurred for a period not exceeding 60 days prior to the date of hospitalization are payable subject to an admissible hospitalization claim."*
  - Full Policy Physical Page 6 (Printed Page 5/47, Definitions): Standard definition of pre-hospitalization medical expenses.
  - Note: Post-hospitalization expenses are covered up to 90 days from discharge (Section B.6).
- **Citations Displayed**: Full Policy Physical Page 11 (Printed Page 10/47), Physical Page 6, Physical Page 14, and Claims Guidance.

### Test 4: Cataract Treatment Terms (Supported - Demonstrates Document Separation)
- **Question**: `"Are cataract treatments subject to specific conditions?"`
- **Expected Status**: `answered` (`is_sufficient_evidence: true`, 3 citations)
- **Verified Policy Clauses**:
  - CIS Physical Page 9 (Printed Page 8/19, Section F.i): Lists cataract and diseases of the eye under specific conditions subject to a 24-month waiting period.
  - Full Policy Physical Page 30 (Printed Page 29/47) & Physical Page 32 (Printed Page 31/47, Section F.i): Confirms 24-month waiting period for cataract; sub-limits apply based on sum insured slab.
- **Citations Displayed**: Shows both documents side-by-side:
  - CIS: `Physical Page 9 (Printed Page 8/19)`
  - Full Policy: `Physical Page 32 (Printed Page 31/47)`

### Test 5: Space Flight (Unsupported - Out of Scope Insurance Claim)
- **Question**: `"Does this policy cover orbital space flight and planetary excursions?"`
- **Expected Status**: `insufficient_evidence` (`is_sufficient_evidence: false`, 0 citations)
- **Expected System Response**:
  - Red/Amber warning banner indicating evidence insufficiency.
  - Explicit statement: *"I cannot verify an answer to your question ('Does this policy cover orbital space flight and planetary excursions?') from the available policy documents or claims guidance. The system strictly abstains when verified evidence is absent..."*
  - Disclaimer: *"Note that the absence of a search match does not prove that a condition is excluded or not covered—please verify with official Star Health policy wording."*

### Test 6: Sourdough Bread Baking (Unsupported - Completely Unrelated Inquiry)
- **Question**: `"How do I bake sourdough bread at high altitude?"`
- **Expected Status**: `insufficient_evidence` (`is_sufficient_evidence: false`, 0 citations)
- **Expected Behavior**: Even though words like "at" or "high" might match generic texts, the multi-keyword threshold in `backend/app/services/qa.py` rejects non-insurance queries and returns clean abstention with zero citations.

---

## 4. How to Demonstrate Specific Platform Features

### 4.1 Demonstrating Source Citations
1. In the **Ask a Policy Question** tab, submit any supported question.
2. Scroll to the **"Verified Source Citations"** section.
3. Click on any citation card to expand it.
4. Point out to evaluators:
   - **Document Title & Type Badge**: Differentiates `Full Policy` from `CIS` and `Claims Guidance`.
   - **Page Accuracy Label**: Highlight `Physical Page 41 (Printed Page 40/47)` and explain that page 1 of the PDF is an unnumbered cover, so printed numbering starts at page 2.
   - **Policy Version**: Explicitly displays `POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)`.
   - **Verbatim Excerpt**: Highlights the exact clause extracted from the PDF.
   - **Integrity Hash**: Shows the SHA-256 fingerprint (`content_hash`) guaranteeing the text was not modified.

### 4.2 Demonstrating Policy Search
1. Click the **Search Policy Documents** navigation tab.
2. Enter `maternity` or `room rent` in the search bar.
3. Demonstrate filtering by document type using the pills (`All Documents`, `Policy Terms`, `Customer Information Sheet (CIS)`).
4. Point out the bold search highlights generated by SQLite FTS5 snippets (`<b>maternity</b>`).
5. Open the **"Active Policy Documents Catalogue"** collapsible drawer to show all 7 indexed documents and their chunk counts.

### 4.3 Demonstrating Claims Guidance
1. Click the **Claims Guidance** navigation tab.
2. Select **Cashless Hospitalisation Procedure**.
3. Walk through the 4-step workflow (Emergency vs Planned Hospitalisation, TPA desk submission, Pre-authorization, Settlement at discharge).
4. Click on the **"Search Cashless Policy Terms"** quick action button to show seamless routing into Policy Search.
5. Highlight the mandatory disclaimer: Guidance is educational and does not constitute guarantee of claim approval.

### 4.4 Demonstrating the Hospital Explorer
1. Click the **Explore Hospitals** navigation tab.
2. Show the **"National Hospital Directory"** tab:
   - Contains 29,974 government-registered public hospitals.
   - Filter by State (e.g., select `Karnataka` or `Maharashtra`).
   - Search for a specific hospital (e.g., `Apollo` or `General Hospital`).
3. Switch to the **"Star Health Cashless Network"** tab:
   - Contains 10 verified network hospitals from Bangalore.
   - Point out the link badge: only unambiguous matches are linked to general directory facilities; uncertain name matches remain separate.
4. Draw attention to the top alert banner:
   > *"Important Distinction: Inclusion in the Government Hospital Directory does NOT establish Star Health network membership. Cashless treatment is only available at verified network hospitals."*

---

## 5. What to Say About the Limited Network Dataset

If evaluators ask why the Star Health network table has only 10 records while the general hospital directory has nearly 30,000, provide this clear, professional explanation:

> *"The Government Hospital Directory (29,974 records) comes from the official open-data national registry of healthcare providers across India.*  
>  
> *In contrast, proprietary insurer cashless network lists (like Star Health's) are not published as bulk open datasets. They are served behind dynamic geographic search portals or published in local PDF/HTML provider directories. We extracted and parsed 10 sample network hospital records from offline provider cards in Bangalore to model and test the insurer network schema, foreign-key linkage, and UI separation.*  
>  
> *Rather than falsely presenting those 10 records as a complete nationwide network, our architecture explicitly separates the two datasets and displays prominent disclaimers. In production, this table would be populated via an automated batch pipeline or insurer B2B API."*

---

## 6. Likely Evaluator Questions and Accurate Answers

### Q1: "Why did you use a deterministic retrieval guidance model instead of OpenAI or Claude?"
**Answer**:
> *"For high-stakes healthcare and insurance domains, ungrounded generative models present severe risks of hallucinating non-existent coverage, misleading waiting periods, or inventing claim approvals. Because no paid external API key is configured in this deployment environment, we implemented a deterministic extractive retrieval model (`provider: "retrieval_grounded_guidance"`). It extracts verbatim clauses from indexed PDF chunks, formats them by document type, and provides strict citations with zero risk of hallucination. The backend is designed with a service interface so an LLM adapter with strict prompt grounding can be plugged in immediately without altering API contracts."*

### Q2: "How do you calculate printed page numbers from the PDF?"
**Answer**:
> *"Both the Customer Information Sheet (CIS) and the Full Policy Wording contain an unnumbered cover page as Physical Page 1. The printed page numbering begins on Physical Page 2 as `1 / 47` in the full policy and `1 / 19` in the CIS. Our ingestion pipeline and search service (`backend/app/search.py::format_page_label`) dynamically inspect the `document_type`: for a full policy chunk on physical page 41, it calculates `printed = 41 - 1 = 40` and formats the label as `Physical Page 41 (Printed Page 40/47)`. This enables policyholders to locate the exact clause in their printed policy booklet."*

### Q3: "What prevents the search engine from returning false positives on unrelated questions?"
**Answer**:
> *"We implemented a multi-stage validation in `backend/app/services/qa.py`:*  
> 1. *Domain token filtering: Common words and query stopwords are stripped.*  
> 2. *Phrase expansion: Conversational phrases like 'before hospitalization' are expanded to insurance terms like 'pre hospitalization'.*  
> 3. *Multi-keyword overlap threshold: For queries with three or more keywords, the system requires at least two keywords to match the candidate chunk. A query like 'How do I bake sourdough bread at high altitude?' fails the overlap threshold against medical insurance text, causing the engine to cleanly abstain with 0 citations."*

### Q4: "Can a user submit an insurance claim through this platform?"
**Answer**:
> *"No. The platform is an informational intelligence and decision-support tool. It does not submit claims, authenticate policyholder accounts, or interact with Star Health's transactional claims processing API. The Claims Guidance module provides step-by-step procedural checklists based on official IRDAI and Star Health documentation, accompanied by clear disclaimers that pre-authorization remains subject to insurer approval."*

### Q5: "How does the system ensure data idempotency during ingestion?"
**Answer**:
> *"Every chunk in `document_chunks` has a unique constraint on `(document_id, chunk_index)` and stores a SHA-256 `content_hash`. When `scripts/ingest_all.py` or `scripts/ingest_policies.py` runs, it clears and re-indexes existing document records rather than creating duplicates. Re-running the entire pipeline keeps the database at exactly 263 chunks and 30,000 entities without duplication."*

### Q6: "What tests exist to prove system correctness?"
**Answer**:
> *"We have 27 automated backend tests across 6 test modules (`backend/tests/`):*  
> - *Database models and foreign key cascading (6 tests)*  
> - *API endpoints, pagination, and error envelopes (5 tests)*  
> - *Ingestion idempotency and MHTML extraction (6 tests)*  
> - *Grounded Q&A, source separation, citation accuracy, and abstention (10 tests)*  
> *All 27 tests run in under 1 second using isolated in-memory SQLite fixtures, and the frontend builds cleanly with zero TypeScript or Vite errors."*
