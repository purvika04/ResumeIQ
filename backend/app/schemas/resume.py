from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EducationItem(BaseModel):
    degree: str
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None

class WorkExperienceItem(BaseModel):
    title: str
    company: Optional[str] = None
    duration: Optional[str] = None
    years: Optional[float] = None
    description: Optional[str] = None

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []

class SkillItem(BaseModel):
    name: str
    canonical_name: str
    category: str
    evidence_snippet: Optional[str] = None
    confidence: float = 1.0

class ParsedResumeData(BaseModel):
    name: str = "Unknown Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationItem] = []
    work_experience: List[WorkExperienceItem] = []
    skills: List[SkillItem] = []
    projects: List[ProjectItem] = []
    certifications: List[str] = []
    estimated_experience_years: float = 0.0
    experience_uncertain: bool = False

class ResumeUploadResponse(BaseModel):
    filename: str
    file_type: str
    resume_doc_id: str
    candidate_id: str
    candidate_name: str
    skills: List[str] = []
    parsed_data: ParsedResumeData
    message: str = "Resume parsed and stored successfully"
