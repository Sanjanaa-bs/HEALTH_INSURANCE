from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from backend.app.database import Base


class EvaluationResult(Base):
    """Model for storing benchmark test case runs and RAG evaluation metrics."""

    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_suite = Column(String(100), nullable=False, index=True)
    test_case_id = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=True)  # policy_qa, network_lookup, claim_flow
    metric_name = Column(String(100), nullable=False)  # faithfulness, context_recall, accuracy
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False, index=True)
    details = Column(Text, nullable=True)  # JSON or descriptive text

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
