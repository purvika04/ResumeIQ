import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.connection import init_db
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.screening import router as screening_router
from app.api.candidates import router as candidates_router
from app.api.analytics import router as analytics_router
from app.api.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("resumeiq")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing ResumeIQ database...")
    init_db()
    logger.info("ResumeIQ database initialized.")
    yield
    # Shutdown actions
    logger.info("Shutting down ResumeIQ...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Resume Screening & Candidate Ranking System using Sentence-BERT & NLP",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(screening_router, prefix="/api")
app.include_router(candidates_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Welcome to ResumeIQ API",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "version": settings.VERSION,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
