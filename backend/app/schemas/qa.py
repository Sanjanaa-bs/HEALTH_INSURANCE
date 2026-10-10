from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CitationItem(BaseModel):
    """Citation identifying exact document source, version, and page."""
    model_config = ConfigDict(from_attributes=True)

    chunk_id: int
    document_id: int
    document_title: str
    document_type: str  # policy, cis, claim_guidance, faq
    version: Optional[str] = None  # e.g. POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)
    page_number: Optional[int] = None  # Physical PDF page number
    printed_page_number: Optional[int] = None  # Printed page number (e.g. page_number - 1)
    page_label: Optional[str] = None  # e.g. "Physical Page 31 (Printed Page 30/47)"
    section_heading: Optional[str] = None
    supporting_text: str
    content_hash: str


class QuestionRequest(BaseModel):
    """Request payload for evidence-grounded question answering."""
    question: str = Field(..., min_length=1, description="User's insurance question")
    document_type: Optional[str] = Field(None, description="Optional document type filter (policy, cis, claim_guidance, faq)")
    conversation_id: Optional[str] = Field(None, description="Optional conversation session ID")
    max_citations: int = Field(5, ge=1, le=10, description="Maximum citations to return")

    @field_validator("question")
    @classmethod
    def validate_question_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question cannot be empty or whitespace only.")
        return v.strip()


class QuestionResponse(BaseModel):
    """Response payload for evidence-grounded question answering."""
    model_config = ConfigDict(from_attributes=True)

    question: str
    answer: str
    status: str  # "answered", "insufficient_evidence"
    is_sufficient_evidence: bool
    provider: str  # "retrieval_grounded_guidance"
    citations: List[CitationItem]
    disclaimer: str
    conversation_id: str
    created_at: datetime
