from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.resume import EducationItem, WorkExperienceItem, ProjectItem, SkillItem

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationItem] = []
    total_experience_years: float = 0.0
    current_role: Optional[str] = None
    resume_doc_id: Optional[str] = None
    skills: List[SkillItem] = []
    created_at: datetime
    updated_at: datetime
