import os
import json
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.models import Base, Recruiter, Skill
from app.services.skill_extractor import SKILL_TAXONOMY

logger = logging.getLogger(__name__)

def create_db_engine():
    """Initializes SQLAlchemy engine with PostgreSQL or SQLite fallback."""
    target_url = settings.DATABASE_URL
    if target_url.startswith("sqlite"):
        db_path = target_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(target_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
    else:
        # PostgreSQL with connection pooling
        try:
            pg_engine = create_engine(
                target_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            # Test connection
            with pg_engine.connect() as conn:
                logger.info(f"Connected to primary PostgreSQL database at {target_url}")
            return pg_engine
        except Exception as e:
            logger.warning(f"Could not connect to primary database ({e}). Falling back to SQLite.")
            fallback_url = settings.SQLITE_FALLBACK_URL
            db_path = fallback_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            return create_engine(fallback_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables, constraints, default recruiter, and skills taxonomy."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed default recruiter
        recruiter = db.query(Recruiter).first()
        if not recruiter:
            default_recruiter = Recruiter(
                id="recruiter-default-01",
                name="Alex Mercer",
                email="recruiter@resumeiq.ai",
                company="ResumeIQ Tech Corp",
                role="Lead Technical Recruiter",
            )
            db.add(default_recruiter)
            db.commit()

        # Seed initial skills taxonomy
        if db.query(Skill).count() == 0:
            for category, skills_dict in SKILL_TAXONOMY.items():
                for canonical, aliases in skills_dict.items():
                    skill = Skill(
                        id=f"skill-{canonical.lower().replace(' ', '-').replace('/', '-')}",
                        name=canonical,
                        category=category,
                        aliases_json=json.dumps(aliases),
                    )
                    db.merge(skill)
            db.commit()
            logger.info("Seeded canonical skills taxonomy into database.")
    except Exception as e:
        logger.error(f"Error during init_db: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

def get_db():
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
