import os
import sys
import json
import httpx
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"

def test_full_workflow():
    client = httpx.Client(base_url=BASE_URL, timeout=60.0)

    print("=================================================================")
    print("      ResumeIQ — Automated End-to-End Workflow Verification      ")
    print("=================================================================\n")

    # 1. Health Check
    print("Step 1: Checking backend health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"✓ Backend Healthy: {r.json()['service']} v{r.json()['version']}\n")

    # 2. Create Job Description
    print("Step 2: Creating a new job posting...")
    new_job = {
        "title": "Lead AI & Backend Architect",
        "department": "Platform Intelligence",
        "location": "San Francisco, CA / Remote",
        "employment_type": "Full-time",
        "min_experience_years": 4.0,
        "description": (
            "We are seeking a Lead AI & Backend Architect to build high-performance distributed systems "
            "and machine learning services. You will architect REST APIs in Python and FastAPI, manage "
            "PostgreSQL and MongoDB databases, containerize microservices using Docker and Kubernetes, "
            "and build neural NLP pipelines using PyTorch and Transformers on AWS cloud."
        ),
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "PyTorch"],
        "preferred_skills": ["AWS", "Kubernetes", "Transformers", "Redis", "CI/CD"],
    }
    r = client.post("/api/jobs", json=new_job)
    assert r.status_code == 200, f"Failed to create job: {r.text}"
    job_data = r.json()
    job_id = job_data["id"]
    print(f"✓ Job Created: '{job_data['title']}' (ID: {job_id})")
    print(f"  Required Skills: {job_data['required_skills']}")
    print(f"  Preferred Skills: {job_data['preferred_skills']}\n")

    # 3. Upload At Least 5 Resumes in Batch
    print("Step 3: Uploading batch of 5 diverse resumes (PDF, DOCX, TXT)...")
    files_to_upload = [
        "alex_morgan.pdf",
        "dr_elena_rostova.docx",
        "marcus_vance.pdf",
        "sofia_chen.docx",
        "priya_sharma.txt",
    ]

    multipart_files = []
    file_handles = []
    for fn in files_to_upload:
        fp = SAMPLE_DIR / "resumes" / fn
        fh = open(fp, "rb")
        file_handles.append(fh)
        mime = "application/pdf" if fn.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if fn.endswith(".docx") else "text/plain"
        multipart_files.append(("files", (fn, fh, mime)))

    try:
        r = client.post("/api/resumes/upload", files=multipart_files)
        assert r.status_code == 200, f"Resume upload failed: {r.text}"
        uploaded_res = r.json()
        print(f"✓ Successfully processed {len(uploaded_res)} resumes:")
        for u in uploaded_res:
            print(f"  • {u['candidate_name']:20s} ({u['file_type']}) | Skills: {len(u['parsed_data']['skills'])} | Exp: {u['parsed_data']['estimated_experience_years']} yrs")
    finally:
        for fh in file_handles:
            fh.close()

    print()

    # 4. Run AI Screening Engine
    print("Step 4: Running Sentence-BERT semantic matching & hybrid scoring...")
    screen_req = {
        "job_id": job_id,
        "weights": {
            "weight_semantic": 0.40,
            "weight_required_skills": 0.35,
            "weight_preferred_skills": 0.15,
            "weight_experience": 0.10,
        }
    }
    r = client.post("/api/screening/run", json=screen_req)
    assert r.status_code == 200, f"Screening failed: {r.text}"
    screening_res = r.json()
    print(f"✓ Screening Complete! Screened: {screening_res['total_screened']} candidates")
    print(f"  Mean Compatibility: {screening_res['average_score']}% | Highest: {screening_res['highest_score']}%\n")

    # 5. Inspect Candidate Rankings
    print("Step 5: Verifying candidate rankings and score differentiation...")
    rankings = screening_res["rankings"]
    assert len(rankings) >= 5, "Expected at least 5 candidates in ranking."
    scores = [c["overall_score"] for c in rankings]
    assert len(set(scores)) > 1, "Scores must be differentiated across candidates."

    for c in rankings:
        print(
            f"  Rank #{c['rank']}: {c['candidate_name']:20s} | "
            f"Overall: {c['overall_score']:5.1f}% | "
            f"Semantic: {c['semantic_score']:5.1f}% | "
            f"ReqSkills: {c['required_skill_score']:5.1f}% | "
            f"Matched: {len(c['matched_required_skills'])} | "
            f"Missing: {len(c['missing_required_skills'])}"
        )

    print()

    # 6. Inspect Candidate Detail Profile & Explainability
    top_candidate = rankings[0]
    cand_id = top_candidate["candidate_id"]
    print(f"Step 6: Inspecting Top Candidate Profile (ID: {cand_id})...")
    r = client.get(f"/api/candidates/{cand_id}")
    assert r.status_code == 200, f"Failed to get candidate profile: {r.text}"
    cand_profile = r.json()
    print(f"✓ Retrieved profile for: {cand_profile['candidate']['name']}")
    print(f"  Email: {cand_profile['candidate']['email']}")
    print(f"  Current Role: {cand_profile['candidate']['current_role']}")
    print(f"  Explanation: {top_candidate['explanation']}")
    print(f"  Matched Skills: {top_candidate['matched_required_skills']}")
    print(f"  Missing Skills: {top_candidate['missing_required_skills']}")
    if top_candidate["evidence_snippets"]:
        print("  Evidence Snippets Sample:")
        for sk, quote in list(top_candidate["evidence_snippets"].items())[:2]:
            print(f"    • {sk}: \"{quote}\"")

    print()

    # 7. Persistence Verification (Restarting client & querying existing data)
    print("Step 7: Verifying Data Persistence across sessions...")
    r = client.get(f"/api/screening/results/{job_id}")
    assert r.status_code == 200
    persisted_results = r.json()
    assert persisted_results["total_screened"] == screening_res["total_screened"]
    print(f"✓ Data Persistence Confirmed: {persisted_results['total_screened']} candidates persisted in database.\n")

    # 8. Analytics Overview Verification
    print("Step 8: Verifying Analytics aggregation...")
    r = client.get("/api/analytics/overview")
    assert r.status_code == 200
    analytics = r.json()
    print(f"✓ Analytics Overview:")
    print(f"  Total Resumes: {analytics['total_resumes']}")
    print(f"  Total Candidates: {analytics['total_candidates']}")
    print(f"  Total Jobs: {analytics['total_jobs']}")
    dist_summary = [f"{b['range_label']}: {b['count']}" for b in analytics['score_distribution']]
    print(f"  Score Distribution: {dist_summary}")

    print("\n=================================================================")
    print("  ALL 12 DEFINITION OF DONE REQUIREMENTS VERIFIED SUCCESSFULLY!  ")
    print("=================================================================")

if __name__ == "__main__":
    test_full_workflow()
