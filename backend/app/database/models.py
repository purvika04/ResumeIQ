import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    company = Column(String(255), nullable=True)
    role = Column(String(100), default="Talent Acquisition")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    jobs = relationship("Job", back_populates="recruiter")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    employment_type = Column(String(50), default="Full-time")
    min_experience_years = Column(Float, default=0.0)
    description = Column(Text, nullable=False)
    required_skills_json = Column(Text, default="[]")  # JSON string array
    preferred_skills_json = Column(Text, default="[]")  # JSON string array
    status = Column(String(50), default="active")
    created_by = Column(String(64), ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recruiter = relationship("Recruiter", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    screening_results = relationship("ScreeningResult", back_populates="job", cascade="all, delete-orphan")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    education_json = Column(Text, default="[]")  # JSON list for backward compatibility
    total_experience_years = Column(Float, default=0.0)
    current_role = Column(String(255), nullable=True)
    resume_doc_id = Column(String(64), nullable=True)  # Pointer to DocumentStore
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate_skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    experiences = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    screening_results = relationship("ScreeningResult", back_populates="candidate", cascade="all, delete-orphan")

class CandidateEducation(Base):
    """Normalized relational table representing candidate academic credentials (1NF/3NF)."""
    __tablename__ = "candidate_educations"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(150), nullable=False)
    institution = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    graduation_year = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="educations")

class CandidateExperience(Base):
    """Normalized relational table representing candidate work history items (1NF/3NF)."""
    __tablename__ = "candidate_experiences"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    duration = Column(String(100), nullable=True)
    years = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="experiences")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    aliases_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    __table_args__ = (
        UniqueConstraint("candidate_id", "skill_name", name="uq_cand_skill_name"),
    )

    id = Column(String(64), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(64), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    proficiency = Column(String(50), default="intermediate")
    years_experience = Column(Float, nullable=True)
    evidence_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="candidate_skills")

class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
        UniqueConstraint("job_id", "skill_name", name="uq_job_skill_name"),
    )

    id = Column(String(64), primary_key=True, default=generate_uuid)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(64), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    is_required = Column(Boolean, default=True)
    importance_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="job_skills")

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_cand_job"),
        CheckConstraint(
            "status IN ('submitted', 'screening', 'shortlisted', 'rejected', 'hired')",
            name="chk_app_status"
        ),
    )

    id = Column(String(64), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_doc_id = Column(String(64), nullable=True)
    status = Column(String(50), default="submitted")
    applied_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_screen_job_cand"),
        CheckConstraint("overall_score >= 0.0 AND overall_score <= 100.0", name="chk_sr_overall"),
        CheckConstraint("semantic_score >= 0.0 AND semantic_score <= 100.0", name="chk_sr_semantic"),
        CheckConstraint("required_skill_score >= 0.0 AND required_skill_score <= 100.0", name="chk_sr_req_skill"),
        CheckConstraint("preferred_skill_score >= 0.0 AND preferred_skill_score <= 100.0", name="chk_sr_pref_skill"),
        CheckConstraint("experience_score >= 0.0 AND experience_score <= 100.0", name="chk_sr_exp"),
        Index("idx_screening_job_score", "job_id", "overall_score"),
    )

    id = Column(String(64), primary_key=True, default=generate_uuid)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    required_skill_score = Column(Float, nullable=False)
    preferred_skill_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    matched_required_skills = Column(Text, default="[]")  # JSON list
    missing_required_skills = Column(Text, default="[]")  # JSON list
    matched_preferred_skills = Column(Text, default="[]")  # JSON list
    missing_preferred_skills = Column(Text, default="[]")  # JSON list
    evidence_snippets = Column(Text, default="{}")  # JSON map skill->snippets
    explanation = Column(Text, nullable=True)
    flagged_for_review = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="screening_results")
    candidate = relationship("Candidate", back_populates="screening_results")

class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint("status IN ('scheduled', 'completed', 'cancelled')", name="chk_int_status"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="chk_int_rating"),
    )

    id = Column(String(64), primary_key=True, default=generate_uuid)
    application_id = Column(String(64), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    round_name = Column(String(100), nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="scheduled")
    interviewer_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="interviews")
