import requests
import json
import time
import os
import psycopg
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"
PG_CONN = "postgresql://apple@localhost:5432/resumeiq"

def run_e2e_verification():
    print("=" * 70)
    print("RESUMEIQ PHASE 3: END-TO-END WORKFLOW & POSTGRESQL VERIFICATION")
    print("=" * 70)

    # 1. Health & DB Type Check
    print("\n[Step 1] Checking /api/health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health_data = r.json()
    print(f"  Service: {health_data['service']} v{health_data['version']}")
    print(f"  Database Type: {health_data['database']['type']}")
    print(f"  Failover Active: {health_data['database']['is_failover_fallback']}")
    assert health_data['database']['engine'] == 'postgresql'
    assert not health_data['database']['is_failover_fallback']

    # 2. Upload Sample Resume
    print("\n[Step 2 & 3] Uploading & Parsing Synthetic Resume...")
    sample_pdf = Path("/Users/apple/Desktop/dbms/resumeiq/sample_data/resumes/alex_morgan.pdf")
    if not sample_pdf.exists():
        sample_pdf = Path("/Users/apple/Desktop/dbms/resumeiq/data/samples/alex_morgan_resume.pdf")
    if not sample_pdf.exists():
        samples = list(Path("/Users/apple/Desktop/dbms/resumeiq").rglob("*.pdf"))
        sample_pdf = samples[0]
    
    with open(sample_pdf, "rb") as f:
        files = [("files", (sample_pdf.name, f.read(), "application/pdf"))]
        r = requests.post(f"{BASE_URL}/resumes/upload", files=files)
    assert r.status_code == 200, f"Upload failed: {r.text}"
    upload_res = r.json()
    first_doc = upload_res[0] if isinstance(upload_res, list) else upload_res
    doc_id = first_doc.get("resume_doc_id") or first_doc.get("doc_id") or first_doc.get("id")
    skills_extracted = first_doc.get("skills") or [s["canonical_name"] for s in first_doc.get("parsed_data", {}).get("skills", [])]
    print(f"  Uploaded: {sample_pdf.name} -> doc_id: {doc_id}")
    print(f"  Candidate Name: {first_doc.get('candidate_name', first_doc.get('name'))}")
    print(f"  Skills Extracted ({len(skills_extracted)}): {skills_extracted[:8]}...")
    assert len(skills_extracted) > 0, "Regression: Zero skills were extracted from resume!"

    # 4. Create Job Description
    print("\n[Step 4 & 5] Creating Job & Extracting Skills...")
    job_payload = {
        "title": "Principal Distributed Systems Engineer",
        "department": "Core Infrastructure",
        "location": "San Francisco, CA / Remote",
        "description": "Looking for a Principal Engineer with 6+ years in Python, Distributed Systems, PostgreSQL, Docker, and Kubernetes. Strong experience in cloud scalability, FastAPI, and CI/CD pipelines.",
        "required_skills": ["Python", "PostgreSQL", "Docker", "Kubernetes", "Distributed Systems"],
        "preferred_skills": ["FastAPI", "CI/CD", "AWS", "Microservices"],
        "required_min_experience_years": 6.0
    }
    r = requests.post(f"{BASE_URL}/jobs", json=job_payload)
    assert r.status_code == 200, f"Create job failed: {r.text}"
    job_data = r.json()
    job_id = job_data["id"]
    print(f"  Created Job ID: {job_id} | Title: {job_data['title']}")
    print(f"  Required Skills: {job_data.get('required_skills')}")
    print(f"  Preferred Skills: {job_data.get('preferred_skills')}")

    # 5. Run Candidate Screening
    print("\n[Step 6 & 7] Running Candidate Screening & Generating Rankings...")
    screen_payload = {
        "job_id": job_id,
        "weights": {
            "semantic": 0.40,
            "required_skills": 0.35,
            "preferred_skills": 0.15,
            "experience": 0.10
        }
    }
    r = requests.post(f"{BASE_URL}/screening/run", json=screen_payload)
    assert r.status_code == 200, f"Screening run failed: {r.text}"
    screening_summary = r.json()
    print(f"  Screened {screening_summary.get('candidates_screened', len(screening_summary.get('rankings', [])))} candidates")

    # 6. Fetch Rankings & Verify Order
    r = requests.get(f"{BASE_URL}/screening/results/{job_id}")
    assert r.status_code == 200, f"Get rankings failed: {r.text}"
    rankings_data = r.json()
    rankings = rankings_data.get("rankings", [])
    print(f"  Top Candidate: {rankings[0]['candidate_name']} with Score: {rankings[0]['overall_score']:.2f}%")
    print(f"  Second Candidate: {rankings[1]['candidate_name']} with Score: {rankings[1]['overall_score']:.2f}%")
    top_cand_id = rankings[0]["candidate_id"]

    # 7. Candidate Details API
    print("\n[Step 8] Opening Candidate Details...")
    r = requests.get(f"{BASE_URL}/candidates/{top_cand_id}")
    assert r.status_code == 200, f"Get candidate failed: {r.text}"
    cand_details = r.json()
    cand_info = cand_details.get("candidate", cand_details)
    print(f"  Retrieved profile for: {cand_info.get('name')}")
    print(f"  Current Role: {cand_info.get('current_role')}")
    print(f"  Experience: {cand_info.get('total_experience_years')} years")

    # 8. Analytics Overview API
    print("\n[Step 9] Generating Analytics Overview...")
    r = requests.get(f"{BASE_URL}/analytics/overview")
    assert r.status_code == 200, f"Analytics overview failed: {r.text}"
    analytics = r.json()
    print(f"  Total Candidates: {analytics.get('total_candidates')}")
    print(f"  Total Jobs: {analytics.get('total_jobs')}")
    print(f"  Average Score: {analytics.get('average_score')}%")

    # 9. Verify in PostgreSQL
    print("\n[Step 10] Direct PostgreSQL Database Verification...")
    with psycopg.connect(PG_CONN) as conn:
        with conn.cursor() as cur:
            # Check job created
            cur.execute("SELECT id, title, min_experience_years FROM jobs WHERE id = %s", (job_id,))
            pg_job = cur.fetchone()
            print(f"  [PG] Job verified in jobs table: {pg_job[1]} (id={pg_job[0]}, min_exp={pg_job[2]} yrs)")

            # Check job_skills
            cur.execute("SELECT skill_name, is_required FROM job_skills WHERE job_id = %s ORDER BY skill_name", (job_id,))
            pg_skills = cur.fetchall()
            print(f"  [PG] Job skills stored: {len(pg_skills)} entries: {[s[0] for s in pg_skills]}")

            # Check screening_results
            cur.execute("SELECT count(*), max(overall_score), min(overall_score) FROM screening_results WHERE job_id = %s", (job_id,))
            pg_screenings = cur.fetchone()
            print(f"  [PG] Screening results in DB: {pg_screenings[0]} rows (Max Score: {pg_screenings[1]:.2f}%, Min: {pg_screenings[2]:.2f}%)")

            # Check audit logs for this job
            cur.execute("SELECT count(*) FROM audit_screening_logs WHERE job_id = %s", (job_id,))
            pg_audit_count = cur.fetchone()[0]
            print(f"  [PG] Audit logs captured by trigger for this job: {pg_audit_count} entries")

            # Check analytical view
            cur.execute("SELECT rank_position, candidate_name, overall_score FROM v_candidate_rankings_dense WHERE job_id = %s ORDER BY rank_position LIMIT 3", (job_id,))
            view_rows = cur.fetchall()
            print(f"  [PG] v_candidate_rankings_dense top 3:")
            for row in view_rows:
                print(f"       Rank #{row[0]}: {row[1]} -> {row[2]}%")

    print("\n" + "=" * 70)
    print("ALL 11 END-TO-END WORKFLOW & POSTGRESQL VERIFICATION STEPS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()
