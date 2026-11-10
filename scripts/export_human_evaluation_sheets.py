"""
Export Human Evaluation & Benchmark Validation Sheets

This script exports:
1. data/evaluation/generation_quality_human_rating_sheet.csv
   For two independent human raters to score generation quality (Factual, Citation, Completeness, Faithfulness, Hallucination)
   on actual system-extracted answers and retrieved citations across all 65 benchmark questions.

2. data/evaluation/benchmark_answers_human_review_sheet.csv
   For an independent human auditor (other than the automated tools) to inspect, verify,
   and validate the ground truth benchmark questions, citations, and answers.
"""

import csv
import json
import os
import sys
from pathlib import Path

# Ensure workspace root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
settings.LLM_PROVIDER = "fallback"  # Ensure deterministic extractive generation

from backend.app.database import SessionLocal
from backend.app.schemas.qa import QuestionRequest
from backend.app.services.qa import answer_insurance_question

def export_evaluation_sheets():
    benchmark_path = Path("data/evaluation/benchmark_qa_60.json")
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark dataset not found at {benchmark_path}")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_queries = json.load(f)

    db = SessionLocal()

    # 1. Export Generation Quality Human Rating Sheet
    rating_sheet_path = Path("data/evaluation/generation_quality_human_rating_sheet.csv")
    rating_headers = [
        "Question_ID",
        "Category",
        "Question",
        "Expected_Status",
        "Ground_Truth_Summary",
        "System_Status",
        "System_Answer",
        "Retrieved_Citations_Summary",
        "Rater1_Name",
        "Rater1_Factual_Correctness_1to5",
        "Rater1_Citation_Accurate_YN",
        "Rater1_Completeness_1to5",
        "Rater1_Faithfulness_1to5",
        "Rater1_Hallucination_YN",
        "Rater1_Comments",
        "Rater2_Name",
        "Rater2_Factual_Correctness_1to5",
        "Rater2_Citation_Accurate_YN",
        "Rater2_Completeness_1to5",
        "Rater2_Faithfulness_1to5",
        "Rater2_Hallucination_YN",
        "Rater2_Comments",
        "Consensus_Factual_Score",
        "Consensus_Citation_Accurate_YN",
        "Consensus_Completeness_Score",
        "Consensus_Faithfulness_Score",
        "Consensus_Hallucination_YN",
        "Discrepancy_Resolution_Notes"
    ]

    rating_rows = []
    print(f"Generating answers and citations for {len(benchmark_queries)} queries...")

    for item in benchmark_queries:
        q_id = item["id"]
        cat = item["category"]
        q_text = item["question"]
        exp_status = item.get("expected_status", "answered")
        gt_summary = item.get("ground_truth_summary", "")

        # Run through QA pipeline
        req = QuestionRequest(question=q_text, max_citations=5)
        resp = answer_insurance_question(db=db, request=req)

        # Format citations
        cit_summaries = []
        for i, c in enumerate(resp.citations, 1):
            doc = c.document_title or "Doc"
            page = c.page_label or (f"p.{c.page_number}" if c.page_number else "p.?")
            sec = c.section_heading or ""
            text_snippet = (c.supporting_text or "").replace("\n", " ")[:120]
            cit_summaries.append(f"[{i}] {doc} ({page}, {sec}): {text_snippet}...")
        citations_str = " | ".join(cit_summaries) if cit_summaries else "None (Abstained/No Citations)"

        clean_answer = (resp.answer or "").replace("\r\n", " ").replace("\n", " ").strip()

        rating_rows.append([
            q_id,
            cat,
            q_text,
            exp_status,
            gt_summary,
            resp.status,
            clean_answer,
            citations_str,
            "",  # Rater1_Name
            "",  # Rater1_Factual_Correctness_1to5
            "",  # Rater1_Citation_Accurate_YN
            "",  # Rater1_Completeness_1to5
            "",  # Rater1_Faithfulness_1to5
            "",  # Rater1_Hallucination_YN
            "",  # Rater1_Comments
            "",  # Rater2_Name
            "",  # Rater2_Factual_Correctness_1to5
            "",  # Rater2_Citation_Accurate_YN
            "",  # Rater2_Completeness_1to5
            "",  # Rater2_Faithfulness_1to5
            "",  # Rater2_Hallucination_YN
            "",  # Rater2_Comments
            "",  # Consensus_Factual_Score
            "",  # Consensus_Citation_Accurate_YN
            "",  # Consensus_Completeness_Score
            "",  # Consensus_Faithfulness_Score
            "",  # Consensus_Hallucination_YN
            ""   # Discrepancy_Resolution_Notes
        ])

    with open(rating_sheet_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(rating_headers)
        writer.writerows(rating_rows)
    print(f"Exported generation rating sheet: {rating_sheet_path} ({len(rating_rows)} rows)")

    # 2. Export Benchmark Answers Human Review Sheet
    benchmark_review_path = Path("data/evaluation/benchmark_answers_human_review_sheet.csv")
    review_headers = [
        "Question_ID",
        "Category",
        "Question",
        "Expected_Status",
        "Target_Documents",
        "Expected_Page_Numbers",
        "Key_Phrases",
        "Proposed_Ground_Truth_Summary",
        "Auditor_Name",
        "Auditor_Verdict_Status",  # Verified_Correct / Requires_Revision / Ambiguous
        "Auditor_Corrected_Ground_Truth",
        "Auditor_Verified_Page_Numbers",
        "Auditor_Observations_and_Clauses",
        "Auditor_Signoff_Date"
    ]

    review_rows = []
    for item in benchmark_queries:
        review_rows.append([
            item["id"],
            item["category"],
            item["question"],
            item.get("expected_status", "answered"),
            "; ".join(item.get("target_documents", [])),
            ", ".join(str(p) for p in item.get("expected_page_numbers", [])),
            "; ".join(item.get("key_phrases", [])),
            item.get("ground_truth_summary", ""),
            "",  # Auditor_Name
            "",  # Auditor_Verdict_Status
            "",  # Auditor_Corrected_Ground_Truth
            "",  # Auditor_Verified_Page_Numbers
            "",  # Auditor_Observations_and_Clauses
            ""   # Auditor_Signoff_Date
        ])

    with open(benchmark_review_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(review_headers)
        writer.writerows(review_rows)
    print(f"Exported benchmark review sheet: {benchmark_review_path} ({len(review_rows)} rows)")

    db.close()

if __name__ == "__main__":
    export_evaluation_sheets()
