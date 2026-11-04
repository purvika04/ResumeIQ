import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Candidate, CandidateSkill, ScreeningResult, Job
from app.database.document_store import doc_store
from app.schemas.candidate import CandidateResponse
from app.schemas.resume import SkillItem, EducationItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("", response_model=List[CandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    """Retrieves all candidates."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    results = []
    for c in candidates:
        edu_list = []
        if c.education_json:
            try:
                edu_list = [EducationItem(**e) for e in json.loads(c.education_json)]
            except Exception:
                pass

        skills_list = [
            SkillItem(
                name=cs.skill_name,
                canonical_name=cs.skill_name,
                category=cs.category or "General",
                evidence_snippet=cs.evidence_snippet,
            )
            for cs in c.candidate_skills
        ]

        results.append(
            CandidateResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                linkedin_url=c.linkedin_url,
                github_url=c.github_url,
                location=c.location,
                summary=c.summary,
                education=edu_list,
                total_experience_years=c.total_experience_years,
                current_role=c.current_role,
                resume_doc_id=c.resume_doc_id,
                skills=skills_list,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return results

@router.get("/{candidate_id}")
def get_candidate_details(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieves comprehensive candidate profile, parsed sections, and screening history across jobs."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    # Retrieve parsed doc from document store
    parsed_doc = None
    raw_doc = None
    if candidate.resume_doc_id:
        parsed_doc = doc_store.find_by_id("resumes_parsed", candidate.resume_doc_id)
        raw_doc = doc_store.find_by_id("resumes_raw", candidate.resume_doc_id)

    # Screening history across jobs
    screenings = db.query(ScreeningResult).filter(ScreeningResult.candidate_id == candidate.id).all()
    screening_history = []
    for s in screenings:
        job = db.query(Job).filter(Job.id == s.job_id).first()
        screening_history.append({
            "job_id": s.job_id,
            "job_title": job.title if job else "Unknown Job",
            "overall_score": s.overall_score,
            "semantic_score": s.semantic_score,
            "required_skill_score": s.required_skill_score,
            "preferred_skill_score": s.preferred_skill_score,
            "experience_score": s.experience_score,
            "matched_required_skills": json.loads(s.matched_required_skills or "[]"),
            "missing_required_skills": json.loads(s.missing_required_skills or "[]"),
            "matched_preferred_skills": json.loads(s.matched_preferred_skills or "[]"),
            "missing_preferred_skills": json.loads(s.missing_preferred_skills or "[]"),
            "evidence_snippets": json.loads(s.evidence_snippets or "{}"),
            "explanation": s.explanation,
            "flagged_for_review": s.flagged_for_review,
            "flag_reason": s.flag_reason,
            "screened_at": s.created_at,
        })

    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "linkedin_url": candidate.linkedin_url,
            "github_url": candidate.github_url,
            "location": candidate.location,
            "summary": candidate.summary,
            "current_role": candidate.current_role,
            "total_experience_years": candidate.total_experience_years,
            "resume_doc_id": candidate.resume_doc_id,
            "created_at": candidate.created_at,
        },
        "parsed_document": parsed_doc,
        "relational_educations": [
            {"id": e.id, "degree": e.degree, "institution": e.institution, "field_of_study": e.field_of_study, "graduation_year": e.graduation_year}
            for e in candidate.educations
        ],
        "relational_experiences": [
            {"id": exp.id, "title": exp.title, "company": exp.company, "duration": exp.duration, "years": exp.years, "description": exp.description}
            for exp in candidate.experiences
        ],
        "raw_text": raw_doc.get("raw_text") if raw_doc else None,
        "screening_history": screening_history,
    }
