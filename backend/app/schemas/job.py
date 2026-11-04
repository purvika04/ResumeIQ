from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Senior Full Stack Engineer"})
    department: Optional[str] = Field("Engineering", json_schema_extra={"example": "Engineering"})
    location: Optional[str] = Field("Remote", json_schema_extra={"example": "Remote / San Francisco"})
    employment_type: Optional[str] = Field("Full-time", json_schema_extra={"example": "Full-time"})
    min_experience_years: float = Field(0.0, json_schema_extra={"example": 3.0})
    description: str = Field(..., json_schema_extra={"example": "We are looking for a Senior Full Stack Engineer to build scalable APIs and responsive UIs..."})
    required_skills: List[str] = Field(default=[], json_schema_extra={"example": ["Python", "FastAPI", "React", "PostgreSQL"]})
    preferred_skills: List[str] = Field(default=[], json_schema_extra={"example": ["Docker", "AWS", "Kubernetes", "Redis"]})

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    min_experience_years: Optional[float] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    min_experience_years: float
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    status: str
    candidate_count: int = 0
    created_at: datetime
    updated_at: datetime
