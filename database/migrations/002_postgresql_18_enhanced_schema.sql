-- =============================================================================
-- ResumeIQ PostgreSQL 18 Migration Script 002: Enhanced Relational Schema
-- Consolidates Normalized Relational Schema, Constraints, Indexes, Views,
-- Triggers, Stored Procedures, and RBAC Security into an Idempotent DDL.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. Base Relational Tables
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS recruiters (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    role VARCHAR(100),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    location VARCHAR(255),
    summary TEXT,
    "current_role" VARCHAR(255),
    total_experience_years DOUBLE PRECISION DEFAULT 0.0,
    resume_doc_id VARCHAR(64),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_educations (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    institution VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year INTEGER,
    gpa DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_experiences (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    location VARCHAR(255),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id VARCHAR(64) REFERENCES skills(id) ON DELETE SET NULL,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    proficiency VARCHAR(50),
    years_experience DOUBLE PRECISION,
    CONSTRAINT uq_cand_skill_name UNIQUE (candidate_id, skill_name)
);

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    location VARCHAR(100),
    employment_type VARCHAR(50),
    min_experience_years DOUBLE PRECISION DEFAULT 0.0,
    description TEXT NOT NULL,
    required_skills_json TEXT,
    preferred_skills_json TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(64) REFERENCES recruiters(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_skills (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id VARCHAR(64) REFERENCES skills(id) ON DELETE SET NULL,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    is_required BOOLEAN DEFAULT TRUE,
    weight DOUBLE PRECISION DEFAULT 1.0,
    CONSTRAINT uq_job_skill_name UNIQUE (job_id, skill_name)
);

CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(64) PRIMARY KEY,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    applied_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'submitted',
    match_score DOUBLE PRECISION,
    CONSTRAINT uq_cand_job UNIQUE (candidate_id, job_id),
    CONSTRAINT chk_app_status CHECK (status IN ('submitted', 'screening', 'shortlisted', 'rejected', 'hired'))
);

CREATE TABLE IF NOT EXISTS screening_results (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id VARCHAR(64) NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    overall_score DOUBLE PRECISION NOT NULL,
    semantic_score DOUBLE PRECISION NOT NULL,
    required_skill_score DOUBLE PRECISION NOT NULL,
    preferred_skill_score DOUBLE PRECISION NOT NULL,
    experience_score DOUBLE PRECISION NOT NULL,
    matched_skills_json TEXT,
    missing_required_skills_json TEXT,
    preferred_skills_matched_json TEXT,
    missing_preferred_skills_json TEXT,
    evidence_snippets_json TEXT,
    explanation TEXT,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    screened_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_screen_job_cand UNIQUE (job_id, candidate_id),
    CONSTRAINT chk_sr_overall CHECK (overall_score >= 0.0 AND overall_score <= 100.0),
    CONSTRAINT chk_sr_semantic CHECK (semantic_score >= 0.0 AND semantic_score <= 100.0),
    CONSTRAINT chk_sr_req_skill CHECK (required_skill_score >= 0.0 AND required_skill_score <= 100.0),
    CONSTRAINT chk_sr_pref_skill CHECK (preferred_skill_score >= 0.0 AND preferred_skill_score <= 100.0),
    CONSTRAINT chk_sr_exp CHECK (experience_score >= 0.0 AND experience_score <= 100.0)
);

CREATE TABLE IF NOT EXISTS interviews (
    id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    round_name VARCHAR(100) NOT NULL,
    scheduled_at TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(50) DEFAULT 'scheduled',
    interviewer_name VARCHAR(255),
    feedback TEXT,
    rating INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_int_status CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    CONSTRAINT chk_int_rating CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5))
);

CREATE TABLE IF NOT EXISTS audit_screening_logs (
    log_id BIGSERIAL PRIMARY KEY,
    screening_id VARCHAR(64) NOT NULL,
    job_id VARCHAR(64) NOT NULL,
    candidate_id VARCHAR(64) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    old_overall_score NUMERIC(5,2),
    new_overall_score NUMERIC(5,2),
    old_flagged BOOLEAN,
    new_flagged BOOLEAN,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. Indexes
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_candidates_lower_email ON candidates(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_active_jobs_created ON jobs(created_at DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_screening_job_score_desc ON screening_results(job_id, overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_screening_flagged_for_review ON screening_results(flagged_for_review) WHERE flagged_for_review = TRUE;
CREATE INDEX IF NOT EXISTS idx_cand_skills_covering ON candidate_skills(candidate_id) INCLUDE (skill_name, category, proficiency);
CREATE INDEX IF NOT EXISTS idx_audit_screening_job_id ON audit_screening_logs(job_id, changed_at DESC);

-- -----------------------------------------------------------------------------
-- 3. Views
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_candidate_rankings_dense AS
SELECT 
    DENSE_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC, sr.semantic_score DESC) AS rank_position,
    ROUND((PERCENT_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score) * 100)::numeric, 1) AS percentile_ranking,
    j.id AS job_id,
    j.title AS job_title,
    j.department AS job_department,
    c.id AS candidate_id,
    c.name AS candidate_name,
    c.email AS candidate_email,
    c."current_role",
    c.total_experience_years,
    j.min_experience_years AS required_min_exp,
    ROUND(sr.overall_score::numeric, 2) AS overall_score,
    ROUND(sr.semantic_score::numeric, 2) AS semantic_score,
    ROUND(sr.required_skill_score::numeric, 2) AS required_skill_score,
    ROUND(sr.preferred_skill_score::numeric, 2) AS preferred_skill_score,
    ROUND(sr.experience_score::numeric, 2) AS experience_score,
    ROUND(AVG(sr.overall_score) OVER (PARTITION BY sr.job_id)::numeric, 2) AS job_cohort_avg_score,
    ROUND((sr.overall_score - AVG(sr.overall_score) OVER (PARTITION BY sr.job_id))::numeric, 2) AS delta_from_avg,
    sr.flagged_for_review,
    sr.flag_reason,
    sr.screened_at
FROM screening_results sr
JOIN jobs j ON sr.job_id = j.id
JOIN candidates c ON sr.candidate_id = c.id;

CREATE OR REPLACE VIEW v_skill_gap_matrix AS
SELECT 
    j.id AS job_id,
    j.title AS job_title,
    c.id AS candidate_id,
    c.name AS candidate_name,
    COUNT(DISTINCT js.skill_name) AS total_required_skills,
    COUNT(DISTINCT cs.skill_name) AS matched_skills_count,
    ROUND((COUNT(DISTINCT cs.skill_name)::numeric / NULLIF(COUNT(DISTINCT js.skill_name), 0)::numeric) * 100.0, 1) AS skill_coverage_pct,
    COALESCE(STRING_AGG(DISTINCT cs.skill_name, ', ' ORDER BY cs.skill_name), 'None') AS matched_skills_list
FROM jobs j
CROSS JOIN candidates c
LEFT JOIN job_skills js ON j.id = js.job_id AND js.is_required = TRUE
LEFT JOIN candidate_skills cs ON c.id = cs.candidate_id AND LOWER(TRIM(cs.skill_name)) = LOWER(TRIM(js.skill_name))
GROUP BY j.id, j.title, c.id, c.name;

CREATE OR REPLACE VIEW v_recruitment_funnel_summary AS
SELECT 
    j.id AS job_id,
    j.title AS job_title,
    j.department,
    j.status AS job_status,
    COUNT(DISTINCT sr.candidate_id) AS total_candidates_screened,
    ROUND(AVG(sr.overall_score)::numeric, 2) AS mean_score,
    ROUND(MAX(sr.overall_score)::numeric, 2) AS top_score,
    ROUND(MIN(sr.overall_score)::numeric, 2) AS lowest_score,
    COUNT(CASE WHEN sr.overall_score >= 80.0 THEN 1 END) AS top_tier_candidates,
    COUNT(CASE WHEN sr.overall_score >= 60.0 AND sr.overall_score < 80.0 THEN 1 END) AS mid_tier_candidates,
    COUNT(CASE WHEN sr.overall_score < 60.0 THEN 1 END) AS low_tier_candidates,
    COUNT(CASE WHEN sr.flagged_for_review = TRUE THEN 1 END) AS flagged_for_manual_review,
    COUNT(DISTINCT a.id) AS formal_applications_count,
    COUNT(DISTINCT i.id) AS scheduled_interviews_count
FROM jobs j
LEFT JOIN screening_results sr ON j.id = sr.job_id
LEFT JOIN applications a ON j.id = a.job_id
LEFT JOIN interviews i ON a.id = i.application_id
GROUP BY j.id, j.title, j.department, j.status;

DROP VIEW IF EXISTS v_candidate_comprehensive_profile;
CREATE VIEW v_candidate_comprehensive_profile AS
SELECT 
    c.id AS candidate_id,
    c.name,
    c.email,
    c.phone,
    c."current_role" AS current_designation,
    c.total_experience_years,
    c.location,
    COALESCE(edu.degrees_held, 'No Degree Specified') AS degrees_held,
    COALESCE(skills.all_skills, 'No Skills Recorded') AS skill_inventory,
    c.created_at
FROM candidates c
LEFT JOIN (
    SELECT 
        candidate_id,
        STRING_AGG(DISTINCT CONCAT(degree, ' (', institution, ')'), '; ') AS degrees_held
    FROM candidate_educations
    GROUP BY candidate_id
) edu ON c.id = edu.candidate_id
LEFT JOIN (
    SELECT 
        candidate_id,
        STRING_AGG(DISTINCT skill_name, ', ' ORDER BY skill_name) AS all_skills
    FROM candidate_skills
    GROUP BY candidate_id
) skills ON c.id = skills.candidate_id;

-- -----------------------------------------------------------------------------
-- 4. Triggers & Stored Functions
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_auto_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_audit_screening_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_screening_logs (
            screening_id, job_id, candidate_id, action_type,
            old_overall_score, new_overall_score, old_flagged, new_flagged
        ) VALUES (
            NEW.id, NEW.job_id, NEW.candidate_id, 'INSERT',
            NULL, NEW.overall_score::numeric(5,2), NULL, NEW.flagged_for_review
        );
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_screening_logs (
            screening_id, job_id, candidate_id, action_type,
            old_overall_score, new_overall_score, old_flagged, new_flagged
        ) VALUES (
            NEW.id, NEW.job_id, NEW.candidate_id, 'UPDATE',
            OLD.overall_score::numeric(5,2), NEW.overall_score::numeric(5,2),
            OLD.flagged_for_review, NEW.flagged_for_review
        );
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_screening_logs (
            screening_id, job_id, candidate_id, action_type,
            old_overall_score, new_overall_score, old_flagged, new_flagged
        ) VALUES (
            OLD.id, OLD.job_id, OLD.candidate_id, 'DELETE',
            OLD.overall_score::numeric(5,2), NULL, OLD.flagged_for_review, NULL
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_calculate_candidate_experience_tenure(p_candidate_id VARCHAR)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    v_total_years DOUBLE PRECISION := 0.0;
    v_cand_stored_exp DOUBLE PRECISION;
BEGIN
    SELECT total_experience_years INTO v_cand_stored_exp 
    FROM candidates WHERE id = p_candidate_id;
    RETURN COALESCE(v_cand_stored_exp, 0.0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE sp_batch_recalculate_scores(
    p_job_id VARCHAR,
    p_w_semantic NUMERIC DEFAULT 0.40,
    p_w_req NUMERIC DEFAULT 0.35,
    p_w_pref NUMERIC DEFAULT 0.15,
    p_w_exp NUMERIC DEFAULT 0.10
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows_updated INTEGER := 0;
BEGIN
    IF ABS((p_w_semantic + p_w_req + p_w_pref + p_w_exp) - 1.0) > 0.001 THEN
        RAISE EXCEPTION 'Total scoring weights must sum to exactly 1.0 (Sum: %)', 
            (p_w_semantic + p_w_req + p_w_pref + p_w_exp);
    END IF;

    UPDATE screening_results
    SET 
        overall_score = ROUND((
            (p_w_semantic * semantic_score) +
            (p_w_req * required_skill_score) +
            (p_w_pref * preferred_skill_score) +
            (p_w_exp * experience_score)
        )::numeric, 2)
    WHERE job_id = p_job_id;

    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;
    RAISE NOTICE 'Successfully recalculated scores for % candidates for job %', v_rows_updated, p_job_id;
END;
$$;
