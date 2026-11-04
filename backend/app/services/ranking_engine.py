import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database.models import Job, Candidate, ScreeningResult
from app.database.document_store import doc_store
from app.schemas.screening import (
    ScoringWeights,
    CandidateRankingItem,
    ScreeningSummaryResponse,
)
from app.services.scoring_engine import scoring_engine

logger = logging.getLogger(__name__)

class RankingEngine:
    """Orchestrates candidate scoring, ranking, persistence, and explainability summaries."""

    def run_screening_for_job(
        self,
        db: Session,
        job_id: str,
        candidate_ids: Optional[List[str]] = None,
        weights: Optional[ScoringWeights] = None,
    ) -> ScreeningSummaryResponse:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job with ID '{job_id}' not found.")

        # Decode job skills
        try:
            req_skills = json.loads(job.required_skills_json) if job.required_skills_json else []
        except Exception:
            req_skills = []
        try:
            pref_skills = json.loads(job.preferred_skills_json) if job.preferred_skills_json else []
        except Exception:
            pref_skills = []

        # Query candidates
        cand_query = db.query(Candidate)
        if candidate_ids:
            cand_query = cand_query.filter(Candidate.id.in_(candidate_ids))
        candidates = cand_query.all()

        if not candidates:
            return ScreeningSummaryResponse(
                job_id=job.id,
                job_title=job.title,
                total_screened=0,
                average_score=0.0,
                highest_score=0.0,
                weights_applied=weights or scoring_engine.default_weights,
                rankings=[],
            )

        scored_items: List[CandidateRankingItem] = []

        for candidate in candidates:
            # Retrieve parsed resume and raw text from document store
            raw_text = ""
            parsed_doc = None
            if candidate.resume_doc_id:
                raw_doc = doc_store.find_by_id("resumes_raw", candidate.resume_doc_id)
                if raw_doc:
                    raw_text = raw_doc.get("raw_text", "")
                parsed_doc = doc_store.find_by_id("resumes_parsed", candidate.resume_doc_id)

            if not raw_text:
                # Fallback to candidate summary and education fields
                raw_text = f"{candidate.name}\n{candidate.summary or ''}\n{candidate.education_json or ''}"

            candidate_skills = []
            if parsed_doc and "skills" in parsed_doc:
                candidate_skills = parsed_doc["skills"]
            else:
                # Fallback to candidate_skills table
                for cs in candidate.candidate_skills:
                    candidate_skills.append({
                        "name": cs.skill_name,
                        "canonical_name": cs.skill_name,
                        "category": cs.category or "General",
                        "evidence_snippet": cs.evidence_snippet or "",
                    })

            is_uncertain = False
            if parsed_doc:
                is_uncertain = parsed_doc.get("experience_uncertain", False)

            score_res = scoring_engine.calculate_score(
                job_description=job.description,
                job_required_skills=req_skills,
                job_preferred_skills=pref_skills,
                job_min_experience=job.min_experience_years,
                candidate_resume_text=raw_text,
                candidate_skills=candidate_skills,
                candidate_experience_years=candidate.total_experience_years,
                candidate_experience_uncertain=is_uncertain,
                custom_weights=weights,
            )

            # Persist or update ScreeningResult in database
            screening_record = (
                db.query(ScreeningResult)
                .filter(ScreeningResult.job_id == job.id, ScreeningResult.candidate_id == candidate.id)
                .first()
            )

            if not screening_record:
                screening_record = ScreeningResult(
                    job_id=job.id,
                    candidate_id=candidate.id,
                )
                db.add(screening_record)

            screening_record.overall_score = score_res["overall_score"]
            screening_record.semantic_score = score_res["semantic_score"]
            screening_record.required_skill_score = score_res["required_skill_score"]
            screening_record.preferred_skill_score = score_res["preferred_skill_score"]
            screening_record.experience_score = score_res["experience_score"]
            screening_record.matched_required_skills = json.dumps(score_res["matched_required_skills"])
            screening_record.missing_required_skills = json.dumps(score_res["missing_required_skills"])
            screening_record.matched_preferred_skills = json.dumps(score_res["matched_preferred_skills"])
            screening_record.missing_preferred_skills = json.dumps(score_res["missing_preferred_skills"])
            screening_record.evidence_snippets = json.dumps(score_res["evidence_snippets"])
            screening_record.explanation = score_res["explanation"]
            screening_record.flagged_for_review = score_res["flagged_for_review"]
            screening_record.flag_reason = score_res["flag_reason"]

            db.commit()
            db.refresh(screening_record)

            scored_items.append(
                CandidateRankingItem(
                    rank=0,  # Will be assigned after sorting
                    candidate_id=candidate.id,
                    candidate_name=candidate.name,
                    candidate_email=candidate.email,
                    current_role=candidate.current_role,
                    total_experience_years=candidate.total_experience_years,
                    overall_score=score_res["overall_score"],
                    semantic_score=score_res["semantic_score"],
                    required_skill_score=score_res["required_skill_score"],
                    preferred_skill_score=score_res["preferred_skill_score"],
                    experience_score=score_res["experience_score"],
                    matched_required_skills=score_res["matched_required_skills"],
                    missing_required_skills=score_res["missing_required_skills"],
                    matched_preferred_skills=score_res["matched_preferred_skills"],
                    missing_preferred_skills=score_res["missing_preferred_skills"],
                    evidence_snippets=score_res["evidence_snippets"],
                    explanation=score_res["explanation"],
                    flagged_for_review=score_res["flagged_for_review"],
                    flag_reason=score_res["flag_reason"],
                    created_at=screening_record.created_at,
                )
            )

        # Sort candidates descending by overall_score
        scored_items.sort(key=lambda x: x.overall_score, reverse=True)

        # Assign 1-based ranks
        for idx, item in enumerate(scored_items, start=1):
            item.rank = idx

        total = len(scored_items)
        avg_score = round(sum(item.overall_score for item in scored_items) / total, 2) if total else 0.0
        highest = scored_items[0].overall_score if scored_items else 0.0

        return ScreeningSummaryResponse(
            job_id=job.id,
            job_title=job.title,
            total_screened=total,
            average_score=avg_score,
            highest_score=highest,
            weights_applied=weights or scoring_engine.default_weights,
            rankings=scored_items,
        )

# Singleton instance
ranking_engine = RankingEngine()
