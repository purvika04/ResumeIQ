import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResumeIQ"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database Settings
    # Primary: PostgreSQL 18 on localhost; Falls back to SQLite if unreachable
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://apple@localhost:5432/resumeiq")
    SQLITE_FALLBACK_URL: str = os.getenv("SQLITE_FALLBACK_URL", f"sqlite:///{BASE_DIR}/data/resumeiq.db")
    
    # MongoDB Settings: if provided, connects to MongoDB; otherwise falls back to local JSON document store
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "resumeiq_db")
    
    # Document storage directory for local fallback
    DOCUMENT_STORE_DIR: str = os.getenv(
        "DOCUMENT_STORE_DIR", str(BASE_DIR / "data" / "document_store")
    )
    UPLOADS_DIR: str = os.getenv(
        "UPLOADS_DIR", str(BASE_DIR / "data" / "uploads")
    )
    
    # NLP / AI Model Settings
    SENTENCE_TRANSFORMER_MODEL: str = os.getenv(
        "SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_CACHE_SIZE: int = 1000
    
    # Default Scoring Weights
    WEIGHT_SEMANTIC: float = 0.40
    WEIGHT_REQUIRED_SKILLS: float = 0.35
    WEIGHT_PREFERRED_SKILLS: float = 0.15
    WEIGHT_EXPERIENCE: float = 0.10
    
    # Allowed File Extensions & Limits
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    MAX_FILE_SIZE_MB: int = 10

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()
