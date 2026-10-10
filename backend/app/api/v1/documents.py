import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.document import Document, DocumentChunk
from backend.app.schemas.document import (
    DocumentRead,
    DocumentListResponse,
    DocumentChunkRead,
    SearchResponse,
)
from backend.app.schemas.qa import QuestionRequest, QuestionResponse
from backend.app.schemas.common import PaginationMeta
from backend.app.search import search_document_chunks
from backend.app.services.qa import answer_insurance_question

router = APIRouter(tags=["Documents"])


@router.get("/documents", response_model=DocumentListResponse)
def get_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated document catalogue entries with chunk counts."""
    query = db.query(Document)

    if document_type:
        query = query.filter(Document.document_type == document_type.strip().lower())

    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

    offset = (page - 1) * page_size
    docs = query.order_by(Document.id.desc()).offset(offset).limit(page_size).all()

    # Calculate chunk count per document
    items = []
    for doc in docs:
        chunk_count = (
            db.query(func.count(DocumentChunk.id))
            .filter(DocumentChunk.document_id == doc.id)
            .scalar()
            or 0
        )
        items.append(
            DocumentRead(
                id=doc.id,
                title=doc.title,
                document_type=doc.document_type,
                source_path=doc.source_path,
                file_format=doc.file_format,
                file_size_bytes=doc.file_size_bytes,
                version=doc.version,
                is_processed=doc.is_processed,
                chunk_count=chunk_count,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )

    return DocumentListResponse(
        items=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )


@router.get("/documents/search", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., min_length=1, description="Search query string"),
    document_type: Optional[str] = Query(None, description="Filter by document type (policy, cis, claim_guidance, faq)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """Full-text search over indexed document passages with excerpt snippets."""
    results = search_document_chunks(db=db, query_text=q, document_type=document_type, limit=limit)
    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results,
    )


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """Fetch a single document by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
    chunk_count = (
        db.query(func.count(DocumentChunk.id))
        .filter(DocumentChunk.document_id == doc.id)
        .scalar()
        or 0
    )
    return DocumentRead(
        id=doc.id,
        title=doc.title,
        document_type=doc.document_type,
        source_path=doc.source_path,
        file_format=doc.file_format,
        file_size_bytes=doc.file_size_bytes,
        version=doc.version,
        is_processed=doc.is_processed,
        chunk_count=chunk_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunkRead])
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    """Fetch chunks associated with a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )
    return chunks


@router.post("/documents/ask", response_model=QuestionResponse)
def ask_document_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    """
    Evidence-grounded question answering over indexed policy documents.
    Constructs answers strictly from verified retrieved passages and provides citations.
    """
    return answer_insurance_question(db=db, request=request)
