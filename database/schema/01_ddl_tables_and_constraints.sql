-- =============================================================================
-- ResumeIQ — Relational Database Schema DDL & Constraints
-- DBMS Target: PostgreSQL 18+
-- File: 01_ddl_tables_and_constraints.sql
-- Concepts Demonstrated: Normalization (1NF, 2NF, 3NF), Referential Integrity,
-- Check Constraints, Composite Keys, Unique Constraints, Cascading Actions
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. Recruiters Table
-- Represents internal recruitment specialists managing talent acquisition.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recruiters (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    role VARCHAR(100) DEFAULT 'Talent Acquisition',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_recruiters_email UNIQUE (email),
    CONSTRAINT chk_recruiters_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

-- -----------------------------------------------------------------------------
-- 2. Candidates Table
-- Central entity for job applicants. Normalized to 3NF by moving repeating
-- educational credentials and employment history into dedicated child tables.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidates (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    location VARCHAR(255),
    summary TEXT,
    education_json TEXT DEFAULT '[]', -- Retained for API backwards-compatibility
    total_experience_years NUMERIC(4, 1) DEFAULT 0.0,
    "current_role" VARCHAR(255),
    resume_doc_id VARCHAR(64), -- Reference pointer to Document Store (MongoDB/JSON)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_candidates_email UNIQUE (email),
    CONSTRAINT chk_candidates_exp_non_negative CHECK (total_experience_years >= 0.0)
);

-- -----------------------------------------------------------------------------
-- 3. Candidate Educations Table (1NF Normalization)
-- Decomposes multi-valued educational qualifications into atomic records.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate_educations (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL,
    degree VARCHAR(150) NOT NULL,
    institution VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_candidate_educations_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_edu_degree_not_empty CHECK (LENGTH(TRIM(degree)) > 0)
);

-- -----------------------------------------------------------------------------
-- 4. Candidate Work Experiences Table (1NF Normalization)
-- Stores individual historical employment tenures per candidate.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate_experiences (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    duration VARCHAR(100),
    years NUMERIC(4, 1) DEFAULT 0.0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_candidate_experiences_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_exp_years_non_negative CHECK (years IS NULL OR years >= 0.0)
);

-- -----------------------------------------------------------------------------
-- 5. Jobs Table
-- Job postings configured by recruiters with experience and domain requirements.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    location VARCHAR(100),
    employment_type VARCHAR(50) DEFAULT 'Full-time',
    min_experience_years NUMERIC(4, 1) DEFAULT 0.0,
    description TEXT NOT NULL,
    required_skills_json TEXT DEFAULT '[]',
    preferred_skills_json TEXT DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_recruiter
        FOREIGN KEY (created_by) REFERENCES recruiters(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_jobs_status CHECK (status IN ('active', 'closed', 'draft', 'archived')),
    CONSTRAINT chk_jobs_min_exp CHECK (min_experience_years >= 0.0)
);

-- -----------------------------------------------------------------------------
-- 6. Skills Taxonomy Table
-- Central reference table of standard technical competencies and aliases.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    aliases_json TEXT DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_skills_name UNIQUE (name),
    CONSTRAINT chk_skills_category CHECK (category IN (
        'Programming Languages', 'Web Development', 'Databases',
        'Cloud & DevOps', 'AI / ML & Data Science', 'Software Engineering Tools',
        'Cybersecurity', 'General'
    ))
);

-- -----------------------------------------------------------------------------
-- 7. Candidate Skills Table (M:N Relationship Junction)
-- Maps skills verified in candidate resumes with evidence snippets and category.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate_skills (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL,
    skill_id VARCHAR(64),
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    proficiency VARCHAR(50) DEFAULT 'intermediate',
    years_experience NUMERIC(4, 1),
    evidence_snippet TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cand_skills_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cand_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT uq_cand_skill_name UNIQUE (candidate_id, skill_name)
);

-- -----------------------------------------------------------------------------
-- 8. Job Skills Table (M:N Relationship Junction)
-- Defines mandatory vs preferred qualifications per job posting.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS job_skills (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL,
    skill_id VARCHAR(64),
    skill_name VARCHAR(100) NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    importance_weight NUMERIC(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_skills_job
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_job_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT uq_job_skill_name UNIQUE (job_id, skill_name),
    CONSTRAINT chk_job_skill_weight CHECK (importance_weight >= 0.0 AND importance_weight <= 2.0)
);

-- -----------------------------------------------------------------------------
-- 9. Applications Table
-- Tracks formal submission lifecycle of candidate to specific job opening.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL,
    job_id VARCHAR(64) NOT NULL,
    resume_doc_id VARCHAR(64),
    status VARCHAR(50) DEFAULT 'submitted',
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_app_job
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_application_cand_job UNIQUE (candidate_id, job_id),
    CONSTRAINT chk_app_status CHECK (
        status IN ('submitted', 'screening', 'shortlisted', 'rejected', 'hired')
    )
);

-- -----------------------------------------------------------------------------
-- 10. Screening Results Table
-- Stores multi-dimensional Sentence-BERT compatibility scores and explanations.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS screening_results (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL,
    candidate_id VARCHAR(64) NOT NULL,
    overall_score NUMERIC(5, 2) NOT NULL,
    semantic_score NUMERIC(5, 2) NOT NULL,
    required_skill_score NUMERIC(5, 2) NOT NULL,
    preferred_skill_score NUMERIC(5, 2) NOT NULL,
    experience_score NUMERIC(5, 2) NOT NULL,
    matched_required_skills TEXT DEFAULT '[]',
    missing_required_skills TEXT DEFAULT '[]',
    matched_preferred_skills TEXT DEFAULT '[]',
    missing_preferred_skills TEXT DEFAULT '[]',
    evidence_snippets TEXT DEFAULT '{}',
    explanation TEXT,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_screening_job
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_screening_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_screening_job_cand UNIQUE (job_id, candidate_id),
    CONSTRAINT chk_sr_overall CHECK (overall_score >= 0.0 AND overall_score <= 100.0),
    CONSTRAINT chk_sr_semantic CHECK (semantic_score >= 0.0 AND semantic_score <= 100.0),
    CONSTRAINT chk_sr_req_skill CHECK (required_skill_score >= 0.0 AND required_skill_score <= 100.0),
    CONSTRAINT chk_sr_pref_skill CHECK (preferred_skill_score >= 0.0 AND preferred_skill_score <= 100.0),
    CONSTRAINT chk_sr_exp CHECK (experience_score >= 0.0 AND experience_score <= 100.0)
);

-- -----------------------------------------------------------------------------
-- 11. Interviews Table
-- Tracks recruiter and technical evaluation stages.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interviews (
    id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'scheduled',
    interviewer_name VARCHAR(255),
    notes TEXT,
    rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interviews_application
        FOREIGN KEY (application_id) REFERENCES applications(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_interview_status CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    CONSTRAINT chk_interview_rating CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5))
);
