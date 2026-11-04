import json
import logging
from typing import Optional, List, Literal
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Job, Candidate, ScreeningResult
from app.schemas.screening import (
    ScreeningRunRequest,
    ScreeningSummaryResponse,
    CandidateRankingItem,
    ScoringWeights,
)
from app.services.ranking_engine import ranking_engine
from app.services.scoring_engine import scoring_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/screening", tags=["Screening & Ranking"])

@router.post("/run", response_model=ScreeningSummaryResponse)
def run_screening(request: ScreeningRunRequest, db: Session = Depends(get_db)):
    """Runs Sentence-BERT NLP matching and hybrid scoring for candidates against a job."""
    try:
        summary = ranking_engine.run_screening_for_job(
            db=db,
            job_id=request.job_id,
            candidate_ids=request.candidate_ids,
            weights=request.weights,
        )
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running screening for job {request.job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Screening error: {str(e)}")

@router.get("/results/{job_id}", response_model=ScreeningSummaryResponse)
def get_screening_results(
    job_id: str,
    sort_by: Literal["score", "experience", "semantic", "required_skills"] = "score",
    sort_order: Literal["asc", "desc"] = "desc",
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    flagged_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Retrieves ranked screening results for a job with filtering and sorting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    query = db.query(ScreeningResult).filter(ScreeningResult.job_id == job_id)
    if min_score > 0:
        query = query.filter(ScreeningResult.overall_score >= min_score)
    if flagged_only:
        query = query.filter(ScreeningResult.flagged_for_review == True)

    results = query.all()

    items: List[CandidateRankingItem] = []
    for r in results:
        candidate = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        if not candidate:
            continue

        items.append(
            CandidateRankingItem(
                rank=0,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                current_role=candidate.current_role,
                total_experience_years=candidate.total_experience_years,
                overall_score=r.overall_score,
                semantic_score=r.semantic_score,
                required_skill_score=r.required_skill_score,
                preferred_skill_score=r.preferred_skill_score,
                experience_score=r.experience_score,
                matched_required_skills=json.loads(r.matched_required_skills or "[]"),
                missing_required_skills=json.loads(r.missing_required_skills or "[]"),
                matched_preferred_skills=json.loads(r.matched_preferred_skills or "[]"),
                missing_preferred_skills=json.loads(r.missing_preferred_skills or "[]"),
                evidence_snippets=json.loads(r.evidence_snippets or "{}"),
                explanation=r.explanation or "",
                flagged_for_review=r.flagged_for_review or False,
                flag_reason=r.flag_reason,
                created_at=r.created_at,
            )
        )

    # Sorting
    reverse = (sort_order == "desc")
    if sort_by == "score":
        items.sort(key=lambda x: x.overall_score, reverse=reverse)
    elif sort_by == "experience":
        items.sort(key=lambda x: x.total_experience_years, reverse=reverse)
    elif sort_by == "semantic":
        items.sort(key=lambda x: x.semantic_score, reverse=reverse)
    elif sort_by == "required_skills":
        items.sort(key=lambda x: x.required_skill_score, reverse=reverse)

    for idx, item in enumerate(items, start=1):
        item.rank = idx

    total = len(items)
    avg_score = round(sum(i.overall_score for i in items) / total, 2) if total else 0.0
    highest = items[0].overall_score if items else 0.0

    return ScreeningSummaryResponse(
        job_id=job.id,
        job_title=job.title,
        total_screened=total,
        average_score=avg_score,
        highest_score=highest,
        weights_applied=scoring_engine.default_weights,
        rankings=items,
    )
