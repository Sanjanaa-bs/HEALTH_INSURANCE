from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.common import PaginationMeta


class DocumentChunkRead(BaseModel):
    """Schema for individual document chunks."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    text: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    chunk_index: int
    content_hash: str
    token_count: Optional[int] = None
    created_at: datetime


class DocumentRead(BaseModel):
    """Schema for document records."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    document_type: str
    source_path: str
    file_format: str
    file_size_bytes: Optional[int] = None
    version: Optional[str] = None
    is_processed: bool
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""
    model_config = ConfigDict(from_attributes=True)

    items: List[DocumentRead]
    pagination: PaginationMeta


class SearchResultItem(BaseModel):
    """Individual matching document chunk from search."""
    model_config = ConfigDict(from_attributes=True)

    chunk_id: int
    document_id: int
    document_title: str
    document_type: str
    version: Optional[str] = None
    page_number: Optional[int] = None
    printed_page_number: Optional[int] = None
    page_label: Optional[str] = None
    section_heading: Optional[str] = None
    excerpt: str
    content_hash: str


class SearchResponse(BaseModel):
    """Response envelope for full-text document search."""
    model_config = ConfigDict(from_attributes=True)

    query: str
    total_results: int
    results: List[SearchResultItem]

