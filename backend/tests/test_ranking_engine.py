import json
import pytest
from app.database.connection import SessionLocal, init_db
from app.database.models import Job, Candidate
from app.database.document_store import doc_store
from app.services.ranking_engine import ranking_engine

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    db = SessionLocal()
    
    # Create test job
    job = Job(
        id="test-job-rankings",
        title="Python Backend Developer",
        department="Engineering",
        min_experience_years=2.0,
        description="Looking for Python and FastAPI developer with Docker and PostgreSQL.",
        required_skills_json=json.dumps(["Python", "FastAPI"]),
        preferred_skills_json=json.dumps(["Docker"]),
        status="active"
    )
    db.merge(job)

    # Candidate 1: strong match
    c1 = Candidate(
        id="test-cand-strong",
        name="Strong Match Candidate",
        email="strong@test.com",
        total_experience_years=4.0,
        current_role="Senior Python Engineer",
        resume_doc_id="doc-cand-strong"
    )
    db.merge(c1)
    doc_store.insert("resumes_raw", {"id": "doc-cand-strong", "raw_text": "Python and FastAPI engineer with Docker and PostgreSQL."})
    doc_store.insert("resumes_parsed", {
        "id": "doc-cand-strong",
        "name": "Strong Match Candidate",
        "skills": [
            {"canonical_name": "Python", "name": "Python", "category": "Programming Languages"},
            {"canonical_name": "FastAPI", "name": "FastAPI", "category": "Web Development"},
            {"canonical_name": "Docker", "name": "Docker", "category": "Cloud & DevOps"},
        ],
        "estimated_experience_years": 4.0,
    })

    # Candidate 2: weak match
    c2 = Candidate(
        id="test-cand-weak",
        name="Weak Match Candidate",
        email="weak@test.com",
        total_experience_years=1.0,
        current_role="Designer",
        resume_doc_id="doc-cand-weak"
    )
    db.merge(c2)
    doc_store.insert("resumes_raw", {"id": "doc-cand-weak", "raw_text": "Figma graphic design and illustration specialist."})
    doc_store.insert("resumes_parsed", {
        "id": "doc-cand-weak",
        "name": "Weak Match Candidate",
        "skills": [],
        "estimated_experience_years": 1.0,
    })

    db.commit()
    yield db
    db.close()

def test_ranking_candidates_order(setup_db):
    db = setup_db
    summary = ranking_engine.run_screening_for_job(db, "test-job-rankings")

    assert summary.total_screened >= 2
    assert summary.highest_score > 0
    # Candidate 1 should rank higher than Candidate 2
    rankings = summary.rankings
    strong_cand = next((c for c in rankings if c.candidate_id == "test-cand-strong"), None)
    weak_cand = next((c for c in rankings if c.candidate_id == "test-cand-weak"), None)

    assert strong_cand is not None
    assert weak_cand is not None
    assert strong_cand.overall_score > weak_cand.overall_score
    assert strong_cand.rank < weak_cand.rank
