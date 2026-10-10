from typing import Dict, Any
from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    """Real database counts and repository dataset statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_hospitals: int
    total_insurer_records: int
    total_documents: int
    total_document_chunks: int
    total_conversations: int
    total_evaluations: int
    dataset_status: Dict[str, Any]
