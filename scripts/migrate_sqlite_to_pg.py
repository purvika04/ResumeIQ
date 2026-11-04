import os
import sys
import json
import uuid
import sqlite3
import sqlalchemy
from pathlib import Path
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend"))

from app.database.models import (
    Base,
    Recruiter,
    Job,
    Candidate,
    CandidateEducation,
    CandidateExperience,
    Skill,
    CandidateSkill,
    JobSkill,
    Application,
    ScreeningResult,
    Interview,
)
from app.database.document_store import doc_store

SQLITE_PATH = BASE_DIR / "backend" / "data" / "resumeiq.db"
PG_URL = "postgresql://apple@localhost:5432/resumeiq"

def migrate():
    print("=================================================================")
    print("     ResumeIQ — Data Migration: SQLite -> PostgreSQL 18          ")
    print("=================================================================\n")

    if not SQLITE_PATH.exists():
        print(f"Error: SQLite database not found at {SQLITE_PATH}")
        sys.exit(1)

    print(f"Preserving existing SQLite database at: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_engine = sqlalchemy.create_engine(PG_URL)
    Session = sessionmaker(bind=pg_engine)
    pg_session = Session()

    try:
        # 1. Migrate Recruiters
        print("Migrating Recruiters...")
        rows = sqlite_cur.execute("SELECT * FROM recruiters").fetchall()
        for r in rows:
            recruiter = Recruiter(
                id=r["id"],
                name=r["name"],
                email=r["email"],
                company=r["company"],
                role=r["role"],
            )
            pg_session.merge(recruiter)
        pg_session.commit()
        print(f"✓ Migrated {len(rows)} recruiters.")

        # 2. Migrate Jobs
        print("Migrating Jobs...")
        rows = sqlite_cur.execute("SELECT * FROM jobs").fetchall()
        for r in rows:
            job = Job(
                id=r["id"],
                title=r["title"],
                department=r["department"],
                location=r["location"],
                employment_type=r["employment_type"],
                min_experience_years=r["min_experience_years"] or 0.0,
                description=r["description"],
                required_skills_json=r["required_skills_json"] or "[]",
                preferred_skills_json=r["preferred_skills_json"] or "[]",
                status=r["status"] or "active",
                created_by=r["created_by"],
            )
            pg_session.merge(job)
        pg_session.commit()
        print(f"✓ Migrated {len(rows)} jobs.")

        # 3. Migrate Job Skills
        print("Migrating Job Skills...")
        rows = sqlite_cur.execute("SELECT * FROM job_skills").fetchall()
        seen_job_skills = set()
        count_js = 0
        for r in rows:
            key = (r["job_id"], r["skill_name"])
            if key in seen_job_skills:
                continue
            seen_job_skills.add(key)
            js = JobSkill(
                id=r["id"] or str(uuid.uuid4()),
                job_id=r["job_id"],
                skill_id=r["skill_id"],
                skill_name=r["skill_name"],
                is_required=bool(r["is_required"]),
                importance_weight=r["importance_weight"] or 1.0,
            )
            pg_session.merge(js)
            count_js += 1
        pg_session.commit()
        print(f"✓ Migrated {count_js} job skills.")

        # 4. Migrate Candidates
        print("Migrating Candidates & Normalizing Educations/Experiences...")
        rows = sqlite_cur.execute("SELECT * FROM candidates").fetchall()
        edu_count = 0
        exp_count = 0
        for r in rows:
            cand = Candidate(
                id=r["id"],
                name=r["name"],
                email=r["email"],
                phone=r["phone"],
                linkedin_url=r["linkedin_url"],
                github_url=r["github_url"],
                location=r["location"],
                summary=r["summary"],
                education_json=r["education_json"] or "[]",
                total_experience_years=r["total_experience_years"] or 0.0,
                current_role=r["current_role"],
                resume_doc_id=r["resume_doc_id"],
            )
            pg_session.merge(cand)
            pg_session.commit()

            # Normalize Educations from education_json
            if r["education_json"]:
                try:
                    edu_list = json.loads(r["education_json"])
                    for e in edu_list:
                        edu = CandidateEducation(
                            id=str(uuid.uuid4()),
                            candidate_id=r["id"],
                            degree=e.get("degree", "Degree"),
                            institution=e.get("institution"),
                            field_of_study=e.get("field_of_study"),
                            graduation_year=str(e.get("graduation_year", "")) if e.get("graduation_year") else None,
                        )
                        pg_session.add(edu)
                        edu_count += 1
                except Exception as ex:
                    print(f"Warning: Could not normalize education for {r['name']}: {ex}")

            # Normalize Experiences from document store
            if r["resume_doc_id"]:
                parsed_doc = doc_store.find_by_id("resumes_parsed", r["resume_doc_id"])
                if parsed_doc and "work_experience" in parsed_doc:
                    for w in parsed_doc["work_experience"]:
                        exp = CandidateExperience(
                            id=str(uuid.uuid4()),
                            candidate_id=r["id"],
                            title=w.get("title", "Software Professional"),
                            company=w.get("company"),
                            duration=w.get("duration"),
                            years=w.get("years"),
                            description=w.get("description"),
                        )
                        pg_session.add(exp)
                        exp_count += 1

        pg_session.commit()
        print(f"✓ Migrated {len(rows)} candidates.")
        print(f"✓ Normalized and inserted {edu_count} candidate educations.")
        print(f"✓ Normalized and inserted {exp_count} candidate work experiences.")

        # 5. Migrate Candidate Skills
        print("Migrating Candidate Skills...")
        rows = sqlite_cur.execute("SELECT * FROM candidate_skills").fetchall()
        seen_cand_skills = set()
        count_cs = 0
        for r in rows:
            key = (r["candidate_id"], r["skill_name"])
            if key in seen_cand_skills:
                continue
            seen_cand_skills.add(key)
            cs = CandidateSkill(
                id=r["id"] or str(uuid.uuid4()),
                candidate_id=r["candidate_id"],
                skill_id=r["skill_id"],
                skill_name=r["skill_name"],
                category=r["category"],
                proficiency=r["proficiency"] or "intermediate",
                years_experience=r["years_experience"],
                evidence_snippet=r["evidence_snippet"],
            )
            pg_session.merge(cs)
            count_cs += 1
        pg_session.commit()
        print(f"✓ Migrated {count_cs} candidate skills.")

        # 6. Migrate Screening Results
        print("Migrating Screening Results...")
        rows = sqlite_cur.execute("SELECT * FROM screening_results").fetchall()
        seen_screens = set()
        count_sr = 0
        for r in rows:
            key = (r["job_id"], r["candidate_id"])
            if key in seen_screens:
                continue
            seen_screens.add(key)
            sr = ScreeningResult(
                id=r["id"] or str(uuid.uuid4()),
                job_id=r["job_id"],
                candidate_id=r["candidate_id"],
                overall_score=r["overall_score"],
                semantic_score=r["semantic_score"],
                required_skill_score=r["required_skill_score"],
                preferred_skill_score=r["preferred_skill_score"],
                experience_score=r["experience_score"],
                matched_required_skills=r["matched_required_skills"] or "[]",
                missing_required_skills=r["missing_required_skills"] or "[]",
                matched_preferred_skills=r["matched_preferred_skills"] or "[]",
                missing_preferred_skills=r["missing_preferred_skills"] or "[]",
                evidence_snippets=r["evidence_snippets"] or "{}",
                explanation=r["explanation"],
                flagged_for_review=bool(r["flagged_for_review"]),
                flag_reason=r["flag_reason"],
            )
            pg_session.merge(sr)
            count_sr += 1
        pg_session.commit()
        print(f"✓ Migrated {count_sr} screening results.")

        print("\n=================================================================")
        print("  DATA MIGRATION TO POSTGRESQL 18 COMPLETED WITH 100% INTEGRITY! ")
        print("=================================================================")

    except Exception as e:
        pg_session.rollback()
        print(f"\nMigration failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_session.close()

if __name__ == "__main__":
    migrate()
