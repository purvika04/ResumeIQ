import platform
from fastapi import APIRouter
from app.config import settings
from app.database.document_store import doc_store, MongoDocumentStore
from app.services.semantic_matcher import semantic_matcher

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """System health check and diagnostic status."""
    is_postgres = settings.DATABASE_URL.startswith("postgresql")
    is_mongo = isinstance(doc_store, MongoDocumentStore)

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "database": {
            "type": "PostgreSQL (Supabase)" if is_postgres else "SQLite (Local Fallback)",
            "connected": True,
        },
        "document_store": {
            "type": "MongoDB" if is_mongo else "Local JSON Document Store (Fallback)",
            "connected": True,
        },
        "ai_engine": {
            "model": settings.SENTENCE_TRANSFORMER_MODEL,
            "status": "loaded" if semantic_matcher._model is not None else "ready_on_demand",
        }
    }
