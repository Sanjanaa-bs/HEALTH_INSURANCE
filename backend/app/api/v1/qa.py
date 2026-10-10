from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.qa import QuestionRequest, QuestionResponse
from backend.app.services.qa import answer_insurance_question

router = APIRouter(tags=["Question Answering"])


@router.post("/qa/ask", response_model=QuestionResponse)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    """
    Evidence-grounded question answering over indexed policy documents.
    Constructs answers strictly from verified retrieved passages and provides citations.
    Abstains when evidence is insufficient.
    """
    return answer_insurance_question(db=db, request=request)
