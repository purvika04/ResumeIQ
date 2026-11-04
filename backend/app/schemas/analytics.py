from typing import List, Dict, Any
from pydantic import BaseModel

class ScoreBucket(BaseModel):
    range_label: str  # "0-20", "21-40", "41-60", "61-80", "81-100"
    count: int

class SkillCount(BaseModel):
    skill: str
    count: int
    category: str

class AnalyticsOverviewResponse(BaseModel):
    total_resumes: int
    total_candidates: int
    total_jobs: int
    active_jobs: int
    total_screenings: int
    average_score: float
    score_distribution: List[ScoreBucket]
    top_candidate_skills: List[SkillCount]
    top_demanded_skills: List[SkillCount]
    recent_screenings: List[Dict[str, Any]]
