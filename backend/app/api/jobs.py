import json
import uuid
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Job, JobSkill, ScreeningResult
from app.schemas.job import JobCreate, JobUpdate, JobResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])

def _job_to_response(job: Job, db: Session) -> JobResponse:
    req_skills = json.loads(job.required_skills_json) if job.required_skills_json else []
    pref_skills = json.loads(job.preferred_skills_json) if job.preferred_skills_json else []
    screened_count = db.query(ScreeningResult).filter(ScreeningResult.job_id == job.id).count()

    return JobResponse(
        id=job.id,
        title=job.title,
        department=job.department,
        location=job.location,
        employment_type=job.employment_type,
        min_experience_years=job.min_experience_years,
        description=job.description,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        status=job.status,
        candidate_count=screened_count,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )

@router.post("", response_model=JobResponse)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Creates a new job description with required and preferred skills."""
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        title=job_in.title,
        department=job_in.department,
        location=job_in.location,
        employment_type=job_in.employment_type,
        min_experience_years=job_in.min_experience_years,
        description=job_in.description,
        required_skills_json=json.dumps(job_in.required_skills),
        preferred_skills_json=json.dumps(job_in.preferred_skills),
        status="active",
    )
    db.add(job)
    db.commit()

    # Add JobSkill junction entries (deduplicated)
    seen_skills = set()
    for s in job_in.required_skills:
        clean_s = s.strip()
        if clean_s and clean_s not in seen_skills:
            seen_skills.add(clean_s)
            db.add(JobSkill(job_id=job.id, skill_name=clean_s, is_required=True, importance_weight=1.0))
    for s in job_in.preferred_skills:
        clean_s = s.strip()
        if clean_s and clean_s not in seen_skills:
            seen_skills.add(clean_s)
            db.add(JobSkill(job_id=job.id, skill_name=clean_s, is_required=False, importance_weight=0.5))
    db.commit()
    db.refresh(job)

    return _job_to_response(job, db)

@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """Retrieves all jobs with candidate screening counts."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [_job_to_response(j, db) for j in jobs]

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieves details of a specific job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _job_to_response(job, db)

@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Updates an existing job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job_update.title is not None:
        job.title = job_update.title
    if job_update.department is not None:
        job.department = job_update.department
    if job_update.location is not None:
        job.location = job_update.location
    if job_update.employment_type is not None:
        job.employment_type = job_update.employment_type
    if job_update.min_experience_years is not None:
        job.min_experience_years = job_update.min_experience_years
    if job_update.description is not None:
        job.description = job_update.description
    if job_update.status is not None:
        job.status = job_update.status

    if job_update.required_skills is not None or job_update.preferred_skills is not None:
        db.query(JobSkill).filter(JobSkill.job_id == job.id).delete()
        seen_update_skills = set()
        
        req_list = job_update.required_skills if job_update.required_skills is not None else json.loads(job.required_skills_json or "[]")
        pref_list = job_update.preferred_skills if job_update.preferred_skills is not None else json.loads(job.preferred_skills_json or "[]")

        job.required_skills_json = json.dumps(req_list)
        job.preferred_skills_json = json.dumps(pref_list)

        for s in req_list:
            clean_s = s.strip()
            if clean_s and clean_s not in seen_update_skills:
                seen_update_skills.add(clean_s)
                db.add(JobSkill(job_id=job.id, skill_name=clean_s, is_required=True, importance_weight=1.0))

        for s in pref_list:
            clean_s = s.strip()
            if clean_s and clean_s not in seen_update_skills:
                seen_update_skills.add(clean_s)
                db.add(JobSkill(job_id=job.id, skill_name=clean_s, is_required=False, importance_weight=0.5))

    db.commit()
    db.refresh(job)
    return _job_to_response(job, db)

@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Deletes a job and its associated screening results."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    db.delete(job)
    db.commit()
    return {"message": f"Job '{job_id}' deleted successfully."}
