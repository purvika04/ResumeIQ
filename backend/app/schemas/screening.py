from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ScoringWeights(BaseModel):
    weight_semantic: float = Field(0.40, ge=0.0, le=1.0)
    weight_required_skills: float = Field(0.35, ge=0.0, le=1.0)
    weight_preferred_skills: float = Field(0.15, ge=0.0, le=1.0)
    weight_experience: float = Field(0.10, ge=0.0, le=1.0)

class ScreeningRunRequest(BaseModel):
    job_id: str
    candidate_ids: Optional[List[str]] = None  # None means screen all available candidates
    weights: Optional[ScoringWeights] = None

class CandidateRankingItem(BaseModel):
    rank: int
    candidate_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    current_role: Optional[str] = None
    total_experience_years: float = 0.0
    overall_score: float
    semantic_score: float
    required_skill_score: float
    preferred_skill_score: float
    experience_score: float
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    evidence_snippets: Dict[str, str] = {}
    explanation: str
    flagged_for_review: bool = False
    flag_reason: Optional[str] = None
    created_at: datetime

class ScreeningSummaryResponse(BaseModel):
    job_id: str
    job_title: str
    total_screened: int
    average_score: float
    highest_score: float
    weights_applied: ScoringWeights
    rankings: List[CandidateRankingItem]
