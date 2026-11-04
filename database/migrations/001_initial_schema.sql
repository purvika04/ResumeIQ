-- ResumeIQ PostgreSQL / Supabase Migration
-- 001_initial_schema.sql

-- Enable UUID extension if supported
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Recruiters
CREATE TABLE IF NOT EXISTS recruiters (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    role VARCHAR(100) DEFAULT 'Talent Acquisition',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Candidates
CREATE TABLE IF NOT EXISTS candidates (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    location VARCHAR(255),
    summary TEXT,
    education_json TEXT, -- JSON array of degrees, institutions, years
    total_experience_years NUMERIC(4, 1) DEFAULT 0.0,
    current_role VARCHAR(255),
    resume_doc_id VARCHAR(64), -- Foreign pointer to MongoDB/document store
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Jobs
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    location VARCHAR(100),
    employment_type VARCHAR(50) DEFAULT 'Full-time',
    min_experience_years NUMERIC(4, 1) DEFAULT 0.0,
    description TEXT NOT NULL,
    required_skills_json TEXT, -- JSON array of strings
    preferred_skills_json TEXT, -- JSON array of strings
    status VARCHAR(50) DEFAULT 'active', -- active, closed, draft
    created_by VARCHAR(64) REFERENCES recruiters(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Skills Taxonomy
CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL, -- Programming Languages, Web, Cloud, Databases, AI/ML, DevOps, etc.
    aliases_json TEXT, -- JSON array of alternate names / aliases
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Candidate Skills Junction
CREATE TABLE IF NOT EXISTS candidate_skills (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id VARCHAR(64) REFERENCES skills(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    proficiency VARCHAR(50) DEFAULT 'intermediate',
    years_experience NUMERIC(4, 1),
    evidence_snippet TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Job Skills Junction
CREATE TABLE IF NOT EXISTS job_skills (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id VARCHAR(64) REFERENCES skills(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    importance_weight NUMERIC(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Applications
CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    resume_doc_id VARCHAR(64),
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, screening, shortlisted, rejected, hired
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, job_id)
);

-- 8. Screening Results
CREATE TABLE IF NOT EXISTS screening_results (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    overall_score NUMERIC(5, 2) NOT NULL,
    semantic_score NUMERIC(5, 2) NOT NULL,
    required_skill_score NUMERIC(5, 2) NOT NULL,
    preferred_skill_score NUMERIC(5, 2) NOT NULL,
    experience_score NUMERIC(5, 2) NOT NULL,
    matched_required_skills TEXT, -- JSON array
    missing_required_skills TEXT, -- JSON array
    matched_preferred_skills TEXT, -- JSON array
    missing_preferred_skills TEXT, -- JSON array
    evidence_snippets TEXT, -- JSON dict of skill/topic -> evidence quotes
    explanation TEXT,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, candidate_id)
);

-- 9. Interviews
CREATE TABLE IF NOT EXISTS interviews (
    id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    round_name VARCHAR(100) NOT NULL, -- Initial Screen, Technical 1, System Design, HR
    scheduled_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, completed, cancelled
    interviewer_name VARCHAR(255),
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_candidate ON applications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_screening_job_score ON screening_results(job_id, overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_cand ON candidate_skills(candidate_id);
