import os
import shutil
import uuid
import json
import logging
from typing import List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.database.models import (
    Candidate,
    CandidateSkill,
    CandidateEducation,
    CandidateExperience,
    ScreeningResult,
    Application,
)
from app.database.document_store import doc_store
from app.schemas.resume import ResumeUploadResponse, ParsedResumeData
from app.services.resume_parser import resume_parser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=List[ResumeUploadResponse])
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Uploads multiple resumes (PDF, DOCX, TXT), parses content, extracts skills, and stores records."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    results: List[ResumeUploadResponse] = []
    uploads_dir = Path(settings.UPLOADS_DIR)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' has unsupported extension '{file_ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Validate file size
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds {settings.MAX_FILE_SIZE_MB}MB limit."
            )

        # Save to disk
        unique_filename = f"{uuid.uuid4().hex[:10]}_{file.filename}"
        saved_file_path = uploads_dir / unique_filename
        with open(saved_file_path, "wb") as f:
            f.write(contents)

        try:
            # Parse resume text and extract entities
            raw_text, parsed_data = resume_parser.parse(str(saved_file_path))

            # Store in Document Store (MongoDB or local fallback)
            resume_doc_id = str(uuid.uuid4())
            raw_doc = {
                "id": resume_doc_id,
                "filename": file.filename,
                "file_type": file_ext,
                "file_path": str(saved_file_path),
                "raw_text": raw_text,
                "file_size_bytes": len(contents),
            }
            doc_store.insert("resumes_raw", raw_doc)

            parsed_doc = {
                "id": resume_doc_id,
                "resume_id": resume_doc_id,
                "name": parsed_data.name,
                "email": parsed_data.email,
                "phone": parsed_data.phone,
                "linkedin_url": parsed_data.linkedin_url,
                "github_url": parsed_data.github_url,
                "summary": parsed_data.summary,
                "education": [e.model_dump() for e in parsed_data.education],
                "work_experience": [w.model_dump() for w in parsed_data.work_experience],
                "skills": [s.model_dump() for s in parsed_data.skills],
                "projects": [p.model_dump() for p in parsed_data.projects],
                "certifications": parsed_data.certifications,
                "estimated_experience_years": parsed_data.estimated_experience_years,
                "experience_uncertain": parsed_data.experience_uncertain,
            }
            doc_store.insert("resumes_parsed", parsed_doc)

            # Insert or update Candidate record in relational DB
            candidate = None
            if parsed_data.email:
                candidate = db.query(Candidate).filter(Candidate.email == parsed_data.email).first()

            if not candidate:
                candidate = Candidate(
                    id=str(uuid.uuid4()),
                    name=parsed_data.name,
                    email=parsed_data.email or f"candidate_{uuid.uuid4().hex[:6]}@example.com",
                    phone=parsed_data.phone,
                    linkedin_url=parsed_data.linkedin_url,
                    github_url=parsed_data.github_url,
                    summary=parsed_data.summary,
                    education_json=json.dumps([e.model_dump() for e in parsed_data.education]),
                    total_experience_years=parsed_data.estimated_experience_years,
                    current_role=parsed_data.work_experience[0].title if parsed_data.work_experience else "Software Professional",
                    resume_doc_id=resume_doc_id,
                )
                db.add(candidate)
            else:
                candidate.name = parsed_data.name
                candidate.phone = parsed_data.phone or candidate.phone
                candidate.linkedin_url = parsed_data.linkedin_url or candidate.linkedin_url
                candidate.github_url = parsed_data.github_url or candidate.github_url
                candidate.summary = parsed_data.summary or candidate.summary
                candidate.education_json = json.dumps([e.model_dump() for e in parsed_data.education])
                candidate.total_experience_years = parsed_data.estimated_experience_years
                candidate.resume_doc_id = resume_doc_id
                if parsed_data.work_experience:
                    candidate.current_role = parsed_data.work_experience[0].title

            db.commit()
            db.refresh(candidate)

            # Replace candidate skills (deduplicated by canonical skill name)
            db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate.id).delete()
            seen_skills = set()
            for s in parsed_data.skills:
                if s.canonical_name in seen_skills:
                    continue
                seen_skills.add(s.canonical_name)
                cand_skill = CandidateSkill(
                    candidate_id=candidate.id,
                    skill_name=s.canonical_name,
                    category=s.category,
                    evidence_snippet=s.evidence_snippet,
                )
                db.add(cand_skill)

            # Replace candidate educations (normalized table)
            db.query(CandidateEducation).filter(CandidateEducation.candidate_id == candidate.id).delete()
            for edu in parsed_data.education:
                cand_edu = CandidateEducation(
                    candidate_id=candidate.id,
                    degree=edu.degree,
                    institution=edu.institution,
                    field_of_study=edu.field_of_study,
                    graduation_year=str(edu.graduation_year) if edu.graduation_year else None,
                )
                db.add(cand_edu)

            # Replace candidate work experiences (normalized table)
            db.query(CandidateExperience).filter(CandidateExperience.candidate_id == candidate.id).delete()
            for exp in parsed_data.work_experience:
                cand_exp = CandidateExperience(
                    candidate_id=candidate.id,
                    title=exp.title,
                    company=exp.company,
                    duration=exp.duration,
                    years=exp.years,
                    description=exp.description,
                )
                db.add(cand_exp)

            db.commit()

            # Record in NLP logs
            doc_store.insert("nlp_logs", {
                "event_type": "resume_parsing",
                "resume_doc_id": resume_doc_id,
                "candidate_name": parsed_data.name,
                "skills_found_count": len(parsed_data.skills),
                "experience_extracted": parsed_data.estimated_experience_years,
            })

            results.append(
                ResumeUploadResponse(
                    filename=file.filename,
                    file_type=file_ext,
                    resume_doc_id=resume_doc_id,
                    candidate_id=candidate.id,
                    candidate_name=candidate.name,
                    parsed_data=parsed_data,
                    message="Resume parsed and candidate profile created successfully",
                )
            )

        except Exception as e:
            logger.error(f"Error processing file '{file.filename}': {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file '{file.filename}': {str(e)}"
            )

    return results

@router.get("")
def list_resumes():
    """Lists all stored raw resumes with candidate information."""
    raw_resumes = doc_store.find_all("resumes_raw")
    summaries = []
    for r in raw_resumes:
        parsed = doc_store.find_by_id("resumes_parsed", r.get("id"))
        summaries.append({
            "id": r.get("id"),
            "filename": r.get("filename"),
            "file_type": r.get("file_type"),
            "candidate_name": parsed.get("name") if parsed else "Unknown",
            "candidate_email": parsed.get("email") if parsed else None,
            "skills_count": len(parsed.get("skills", [])) if parsed else 0,
            "experience_years": parsed.get("estimated_experience_years", 0.0) if parsed else 0.0,
            "created_at": r.get("created_at"),
        })
    return summaries

@router.get("/{resume_id}")
def get_resume(resume_id: str):
    """Retrieves full raw text and parsed JSON structure for a resume."""
    raw = doc_store.find_by_id("resumes_raw", resume_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Resume not found.")
    parsed = doc_store.find_by_id("resumes_parsed", resume_id)
    return {
        "raw": raw,
        "parsed": parsed,
    }

@router.delete("/{resume_id}")
def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Deletes resume documents and associated records."""
    candidate = db.query(Candidate).filter(Candidate.resume_doc_id == resume_id).first()
    if candidate:
        db.delete(candidate)
        db.commit()

    doc_store.delete("resumes_raw", resume_id)
    doc_store.delete("resumes_parsed", resume_id)
    return {"message": f"Resume '{resume_id}' deleted successfully."}
