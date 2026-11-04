import json
import logging
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.database.models import Job, Candidate, ScreeningResult, CandidateSkill, JobSkill
from app.database.document_store import doc_store
from app.schemas.analytics import AnalyticsOverviewResponse, ScoreBucket, SkillCount

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Computes real-time platform statistics, score distribution, and skill analytics."""
    raw_resumes = doc_store.find_all("resumes_raw")
    total_resumes = len(raw_resumes)
    total_candidates = db.query(Candidate).count()
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.status == "active").count()

    screenings = db.query(ScreeningResult).all()
    total_screenings = len(screenings)

    if screenings:
        avg_score = round(sum(s.overall_score for s in screenings) / total_screenings, 1)
    else:
        avg_score = 0.0

    # Score distribution buckets: 0-20, 21-40, 41-60, 61-80, 81-100
    buckets = {
        "0-20%": 0,
        "21-40%": 0,
        "41-60%": 0,
        "61-80%": 0,
        "81-100%": 0,
    }
    for s in screenings:
        score = s.overall_score
        if score <= 20:
            buckets["0-20%"] += 1
        elif score <= 40:
            buckets["21-40%"] += 1
        elif score <= 60:
            buckets["41-60%"] += 1
        elif score <= 80:
            buckets["61-80%"] += 1
        else:
            buckets["81-100%"] += 1

    score_distribution = [
        ScoreBucket(range_label=label, count=count)
        for label, count in buckets.items()
    ]

    # Top Candidate Skills
    cand_skills = (
        db.query(CandidateSkill.skill_name, CandidateSkill.category, func.count(CandidateSkill.id))
        .group_by(CandidateSkill.skill_name, CandidateSkill.category)
        .order_by(func.count(CandidateSkill.id).desc())
        .limit(10)
        .all()
    )
    top_candidate_skills = [
        SkillCount(skill=row[0], category=row[1] or "General", count=row[2])
        for row in cand_skills
    ]

    # Top Demanded Job Skills
    job_skills = (
        db.query(JobSkill.skill_name, func.count(JobSkill.id))
        .group_by(JobSkill.skill_name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(10)
        .all()
    )
    top_demanded_skills = [
        SkillCount(skill=row[0], category="Required/Preferred", count=row[1])
        for row in job_skills
    ]

    # Recent Screenings
    recent_records = (
        db.query(ScreeningResult)
        .order_by(ScreeningResult.created_at.desc())
        .limit(8)
        .all()
    )
    recent_screenings = []
    for r in recent_records:
        candidate = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        job = db.query(Job).filter(Job.id == r.job_id).first()
        if candidate and job:
            recent_screenings.append({
                "candidate_name": candidate.name,
                "candidate_id": candidate.id,
                "job_title": job.title,
                "job_id": job.id,
                "overall_score": r.overall_score,
                "flagged": r.flagged_for_review,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

    return AnalyticsOverviewResponse(
        total_resumes=total_resumes,
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_screenings=total_screenings,
        average_score=avg_score,
        score_distribution=score_distribution,
        top_candidate_skills=top_candidate_skills,
        top_demanded_skills=top_demanded_skills,
        recent_screenings=recent_screenings,
    )
