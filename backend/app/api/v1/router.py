from fastapi import APIRouter
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.hospitals import router as hospitals_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.qa import router as qa_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(hospitals_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(qa_router)
