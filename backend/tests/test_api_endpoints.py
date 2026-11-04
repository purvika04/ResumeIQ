import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ai_engine" in data
    assert "database" in data

def test_jobs_crud():
    # 1. Create Job
    job_payload = {
        "title": "API Test Job Engineer",
        "department": "Engineering",
        "location": "Remote",
        "min_experience_years": 3.0,
        "description": "Python FastAPI test position for automated endpoint verification.",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["Docker"]
    }
    create_res = client.post("/api/jobs", json=job_payload)
    assert create_res.status_code == 200
    created_job = create_res.json()
    job_id = created_job["id"]
    assert created_job["title"] == "API Test Job Engineer"

    # 2. Get Job
    get_res = client.get(f"/api/jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id

    # 3. List Jobs
    list_res = client.get("/api/jobs")
    assert list_res.status_code == 200
    assert any(j["id"] == job_id for j in list_res.json())

    # 4. Update Job
    update_res = client.put(f"/api/jobs/{job_id}", json={"title": "Updated API Test Job"})
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated API Test Job"

    # 5. Delete Job
    del_res = client.delete(f"/api/jobs/{job_id}")
    assert del_res.status_code == 200

def test_analytics_overview():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_resumes" in data
    assert "total_candidates" in data
    assert "score_distribution" in data
    assert "top_candidate_skills" in data

def test_resume_upload_and_list(tmp_path):
    # Create sample resume text file
    sample_txt = tmp_path / "test_api_candidate.txt"
    sample_txt.write_text(
        "Taylor Swift\n"
        "Email: taylor.swift.dev@example.com\n"
        "Phone: 555-0199\n"
        "Summary: Backend Engineer with 4 years in Python and Docker.\n"
        "Experience\n"
        "2020 - 2024 Backend Developer\n"
        "Built Python APIs and Docker containers.\n"
    )

    with open(sample_txt, "rb") as f:
        files = [("files", ("test_api_candidate.txt", f, "text/plain"))]
        upload_res = client.post("/api/resumes/upload", files=files)

    assert upload_res.status_code == 200
    data = upload_res.json()
    assert len(data) == 1
    assert data[0]["candidate_name"] == "Taylor Swift"

    # Verify resume in list
    list_res = client.get("/api/resumes")
    assert list_res.status_code == 200
    assert any(r["candidate_name"] == "Taylor Swift" for r in list_res.json())
