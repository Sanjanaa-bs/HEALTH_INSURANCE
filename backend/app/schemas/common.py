from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response schema."""
    model_config = ConfigDict(from_attributes=True)

    status: str
    environment: str
    database_connected: bool
    version: str
    timestamp: datetime


class PaginationMeta(BaseModel):
    """Pagination metadata schema."""
    model_config = ConfigDict(from_attributes=True)

    page: int
    page_size: int
    total_items: int
    total_pages: int


class ErrorDetail(BaseModel):
    """Structured error payload."""
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Global API error envelope."""
    error: ErrorDetail
