# Human Evaluation Protocol & Benchmark Audit Guide

**Paper ID:** [907]  
**Title:** *An Offline-Capable Intelligent Assistant for Cashless Hospital Verification and Policy Clause Retrieval*  
**Conference:** ICICF-2027 (JAIN University, Bengaluru)  

---

## 1. Overview & Objectives

In response to the reviewer feedback (Comments 1, 6, and 7) and strict experimental verification standards:
1. **Automated metric numbers are held back from the final camera-ready paper** until the evaluation scripts (`scripts/evaluate_ir_metrics.py`, `scripts/evaluate_generation_quality.py`) are thoroughly audited.
2. **Two independent human evaluators (Rater 1 and Rater 2)** will evaluate generated answers on the exported sheet:
   - File: [`data/evaluation/generation_quality_human_rating_sheet.csv`](file:///c:/Users/sanjana/Downloads/HEALTH_INSURANCE/data/evaluation/generation_quality_human_rating_sheet.csv)
3. **An independent human auditor (other than the tool author)** will verify the ground truth benchmark answers and citations:
   - File: [`data/evaluation/benchmark_answers_human_review_sheet.csv`](file:///c:/Users/sanjana/Downloads/HEALTH_INSURANCE/data/evaluation/benchmark_answers_human_review_sheet.csv)

---

## 2. Evaluation Task 1: Double-Blind Human Rating of Generation Quality

### File to Use
- **File:** `data/evaluation/generation_quality_human_rating_sheet.csv`
- Contains **65 benchmark questions**, expected status, ground-truth summary, actual system extracted answers, and retrieved citations.

### Rater Responsibilities
- **Rater 1** fills columns:
  - `Rater1_Name`: Annotator name or identifier
  - `Rater1_Factual_Correctness_1to5`: (1 to 5 Likert Scale)
  - `Rater1_Citation_Accurate_YN`: (Y or N)
  - `Rater1_Completeness_1to5`: (1 to 5 Likert Scale)
  - `Rater1_Faithfulness_1to5`: (1 to 5 Likert Scale)
  - `Rater1_Hallucination_YN`: (Y or N)
  - `Rater1_Comments`: Optional observations
- **Rater 2** fills columns:
  - `Rater2_Name`
  - `Rater2_Factual_Correctness_1to5`
  - `Rater2_Citation_Accurate_YN`
  - `Rater2_Completeness_1to5`
  - `Rater2_Faithfulness_1to5`
  - `Rater2_Hallucination_YN`
  - `Rater2_Comments`

### Scoring Rubrics

#### A. Factual Correctness (1–5 Scale)
- **5 (Completely Factual):** All facts, limits, timeframes, and terms match the underlying policy terms exactly.
- **4 (Mostly Factual):** Correct on core terms; minor benign phrasing difference.
- **3 (Partially Correct):** Core rule is correct but misses a relevant sub-clause (e.g., states ICU is covered but omits ICU room cap condition).
- **2 (Major Factual Errors):** Distorts waiting periods, deductibles, or policy restrictions.
- **1 (Completely Inaccurate):** Fabricates non-existent coverage or asserts the opposite of the policy rule.

#### B. Citation Accuracy (Y/N)
- **Y (Accurate):** Citations point to the actual document and page containing the authoritative clause.
- **N (Inaccurate):** Citations point to wrong documents, irrelevant sections, or non-existent pages.

#### C. Completeness (1–5 Scale)
- **5 (Comprehensive):** Fully answers the question including mandatory waiting periods, sub-limits, and conditions.
- **4 (Sufficient):** Answers the primary question with standard details.
- **3 (Partial):** Missing important context (e.g., mentions 24-month waiting period but omits specific named illnesses).
- **2 (Incomplete):** Superficial answer lacking essential guidance.
- **1 (Deficient/Empty):** Fails to address the question.

#### D. Faithfulness (1–5 Scale)
- **5 (Strictly Entailed):** Every single sentence and claim is directly traceable to the cited text excerpt.
- **4 (Essentially Grounded):** Minor general knowledge phrasing; all substantive insurance facts are grounded.
- **3 (Mixed):** Contains assertions not verifiable in the retrieved citation.
- **2 (Mostly Ungrounded):** Introduces extraneous rules or external assumptions.
- **1 (Fabricated):** Disconnected from retrieved excerpts.

#### E. Hallucination (Y/N)
- **Y (Hallucinated):** The model invents coverage terms, waiting periods, room rent caps, or claims that are unsupported by the contract.
- **N (No Hallucination):** Output stays strictly bounded by evidence. If evidence is insufficient, it explicitly abstains.

---

## 3. Evaluation Task 2: Independent Benchmark Ground-Truth Audit

### File to Use
- **File:** `data/evaluation/benchmark_answers_human_review_sheet.csv`
- Contains **65 benchmark questions**, targeted document types, expected page numbers, key phrases, and proposed ground truth answers.

### Auditor Responsibilities
An independent human auditor (must NOT be the author of the ingestion tool or retrieval code) checks each row against official policy PDF files:
1. Open the referenced policy PDF (e.g., `Star_Comprehensive_Insurance_Policy_V_24.pdf`, `CIS_Star_Comprehensive_V_24.pdf`, `IRDAI_Master_Circular_2024.pdf`).
2. Verify if the `Expected_Page_Numbers` match the physical page in the PDF and printed page header/footer.
3. Verify if `Proposed_Ground_Truth_Summary` accurately reflects the clause text without bias or distortion.
4. Fill in:
   - `Auditor_Name`: Reviewer name
   - `Auditor_Verdict_Status`: `Verified_Correct`, `Requires_Revision`, or `Ambiguous`
   - `Auditor_Corrected_Ground_Truth`: Corrected text if any discrepancy is found
   - `Auditor_Verified_Page_Numbers`: Confirmed page numbers
   - `Auditor_Observations_and_Clauses`: Clause number (e.g., Section 1.B, Condition 3)
   - `Auditor_Signoff_Date`: Date of signoff

---

## 4. Script Verification Checklist for Item 6 & Item 7

Before pasting the numbers into the camera-ready manuscript:

- [ ] **Check `scripts/evaluate_ir_metrics.py`:**
  - Verify that query text matches `benchmark_qa_60.json`.
  - Verify reciprocal rank calculation $\text{RR} = 1/\text{rank}$.
  - Verify nDCG discounted gain formulation: $\text{DCG}@K = \sum_{i=1}^K \frac{2^{rel_i} - 1}{\log_2(i+1)}$.
  - Verify that SQLite FTS5 index is clean and uncorrupted.
- [ ] **Check `scripts/evaluate_generation_quality.py`:**
  - Verify that deterministic extractive mode tests actual live pipeline outputs (`resp = answer_insurance_question(...)`).
  - Verify that abstention scoring correctly handles out-of-domain queries ($N=12$).
- [ ] **Consensus & Agreement Metrics:**
  - Calculate inter-rater reliability:
    - Cohen's Kappa $\kappa$ for Citation Accuracy and Hallucination ($Y/N$).
    - Pearson $r$ or Spearman $\rho$ for Factual Correctness and Completeness (1–5).
  - Where $|Rater1 - Rater2| \ge 2$, conduct adjudication meeting to record consensus.

---

## 5. Final Step: Inserting Verified Numbers into Paper

Once Rater 1 and Rater 2 finish the spreadsheet and the benchmark answers are validated:
1. Run summary script to compute mean Likert scores, citation accuracy %, and hallucination %.
2. Update Table I in `docs/camera_ready_paper.tex` and Table IV in `docs/REVISED_RESEARCH_PAPER_ICICF2027.md` with verified IR numbers.
3. Update Table IV in `docs/camera_ready_paper.tex` and Table VII in `docs/REVISED_RESEARCH_PAPER_ICICF2027.md` with verified generation quality numbers.
4. Compile final PDF with `pdflatex docs/camera_ready_paper.tex`.

