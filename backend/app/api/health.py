import platform
from fastapi import APIRouter
from app.config import settings
from app.database.connection import get_active_db_info
from app.database.document_store import doc_store, MongoDocumentStore
from app.services.semantic_matcher import semantic_matcher

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """System health check and diagnostic status."""
    db_info = get_active_db_info()
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
            "type": db_info.get("label", "Unknown Database"),
            "engine": db_info.get("engine_name"),
            "host": db_info.get("host"),
            "port": db_info.get("port"),
            "database_name": db_info.get("database"),
            "is_failover_fallback": db_info.get("is_fallback", False),
            "connected": True,
            "pool_status": db_info.get("pool_status"),
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
