from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health check endpoint verifying database connectivity and system status."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        environment=settings.APP_ENV,
        database_connected=db_connected,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )
