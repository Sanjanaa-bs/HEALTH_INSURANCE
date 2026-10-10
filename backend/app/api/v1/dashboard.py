import os
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.models.document import Document, DocumentChunk
from backend.app.models.chat import Conversation
from backend.app.models.evaluation import EvaluationResult
from backend.app.schemas.dashboard import DashboardSummary

router = APIRouter(tags=["Dashboard"])


def get_dataset_filesystem_status() -> dict:
    """Inspect data/ directory for source datasets status without modifying them."""
    base_data = Path("data")
    status = {
        "hospitals_csv_exists": (base_data / "hospitals" / "hospital_directory.csv").exists(),
        "insurer_network_files": 0,
        "policies_files": 0,
        "claim_guidance_files": 0,
        "evaluation_files": 0,
    }

    if (base_data / "insurer_networks").exists():
        status["insurer_network_files"] = len(
            [f for f in (base_data / "insurer_networks").iterdir() if f.is_file()]
        )
    if (base_data / "policies").exists():
        status["policies_files"] = len(
            [f for f in (base_data / "policies").iterdir() if f.is_file()]
        )
    if (base_data / "claim_guidance").exists():
        status["claim_guidance_files"] = len(
            [f for f in (base_data / "claim_guidance").iterdir() if f.is_file()]
        )
    if (base_data / "evaluation").exists():
        status["evaluation_files"] = len(
            [f for f in (base_data / "evaluation").iterdir() if f.is_file()]
        )

    return status


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Return live database counts and source dataset availability."""
    total_hospitals = db.query(func.count(Hospital.id)).scalar() or 0
    total_insurer_records = db.query(func.count(InsurerHospitalRecord.id)).scalar() or 0
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_document_chunks = db.query(func.count(DocumentChunk.id)).scalar() or 0
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
    total_evaluations = db.query(func.count(EvaluationResult.id)).scalar() or 0

    return DashboardSummary(
        total_hospitals=total_hospitals,
        total_insurer_records=total_insurer_records,
        total_documents=total_documents,
        total_document_chunks=total_document_chunks,
        total_conversations=total_conversations,
        total_evaluations=total_evaluations,
        dataset_status=get_dataset_filesystem_status(),
    )
