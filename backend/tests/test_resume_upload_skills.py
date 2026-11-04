import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_resume_upload_extracts_and_returns_skills():
    """Regression test ensuring that resume upload extracts and returns skills at top-level and in parsed_data."""
    sample_pdf = Path("../sample_data/resumes/alex_morgan.pdf")
    if not sample_pdf.exists():
        sample_pdf = Path("sample_data/resumes/alex_morgan.pdf")
    if not sample_pdf.exists():
        sample_pdf = Path("/Users/apple/Desktop/dbms/resumeiq/sample_data/resumes/alex_morgan.pdf")

    assert sample_pdf.exists(), f"Sample PDF not found at {sample_pdf}"

    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/resumes/upload",
            files=[("files", ("alex_morgan.pdf", f.read(), "application/pdf"))]
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    uploaded = data[0]
    # Check top-level fields
    assert uploaded["candidate_name"] == "Alex Morgan"
    assert "resume_doc_id" in uploaded
    assert uploaded["resume_doc_id"] is not None

    # Check that skills are present and non-empty at both levels
    assert "skills" in uploaded
    assert isinstance(uploaded["skills"], list)
    assert len(uploaded["skills"]) >= 10, f"Expected at least 10 skills, got {len(uploaded['skills'])}"
    assert "Python" in uploaded["skills"]
    assert "PostgreSQL" in uploaded["skills"]
    assert "Docker" in uploaded["skills"]

    # Check nested parsed_data
    assert "parsed_data" in uploaded
    assert len(uploaded["parsed_data"]["skills"]) == len(uploaded["skills"])
