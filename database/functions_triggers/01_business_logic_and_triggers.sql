-- =============================================================================
-- ResumeIQ — Stored Procedures, Functions, Triggers & Audit Logging
-- DBMS Target: PostgreSQL 18+
-- File: 01_business_logic_and_triggers.sql
-- Concepts Demonstrated: PL/pgSQL Functions, BEFORE/AFTER Triggers, Audit Tables,
-- Stored Procedures, ACID Transactions, Error Handling (RAISE EXCEPTION)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Audit Trail Table
-- Stores an immutable historical log of all modifications made to screening results.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_screening_logs (
    log_id BIGSERIAL PRIMARY KEY,
    screening_id VARCHAR(64) NOT NULL,
    job_id VARCHAR(64) NOT NULL,
    candidate_id VARCHAR(64) NOT NULL,
    action_type VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_overall_score NUMERIC(5, 2),
    new_overall_score NUMERIC(5, 2),
    old_flagged BOOLEAN,
    new_flagged BOOLEAN,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_screening_job_id
    ON audit_screening_logs (job_id, changed_at DESC);

-- -----------------------------------------------------------------------------
-- 2. Trigger Function: Automatically Update updated_at Timestamp
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_auto_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach timestamp triggers to mutable tables
DROP TRIGGER IF EXISTS trg_recruiters_timestamp ON recruiters;
CREATE TRIGGER trg_recruiters_timestamp
    BEFORE UPDATE ON recruiters
    FOR EACH ROW
    EXECUTE FUNCTION fn_auto_update_timestamp();

DROP TRIGGER IF EXISTS trg_candidates_timestamp ON candidates;
CREATE TRIGGER trg_candidates_timestamp
    BEFORE UPDATE ON candidates
    FOR EACH ROW
    EXECUTE FUNCTION fn_auto_update_timestamp();

DROP TRIGGER IF EXISTS trg_jobs_timestamp ON jobs;
CREATE TRIGGER trg_jobs_timestamp
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION fn_auto_update_timestamp();

-- -----------------------------------------------------------------------------
-- 3. Trigger Function: Audit Trail for Screening Score Modifications
-- Captures state transitions before and after automated or manual overrides.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_audit_screening_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_screening_logs (
            screening_id, job_id, candidate_id, action_type,
            old_overall_score, new_overall_score,
            old_flagged, new_flagged
        ) VALUES (
            NEW.id, NEW.job_id, NEW.candidate_id, 'INSERT',
            NULL, NEW.overall_score,
            NULL, NEW.flagged_for_review
        );
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF (OLD.overall_score != NEW.overall_score OR OLD.flagged_for_review != NEW.flagged_for_review) THEN
            INSERT INTO audit_screening_logs (
                screening_id, job_id, candidate_id, action_type,
                old_overall_score, new_overall_score,
                old_flagged, new_flagged
            ) VALUES (
                NEW.id, NEW.job_id, NEW.candidate_id, 'UPDATE',
                OLD.overall_score, NEW.overall_score,
                OLD.flagged_for_review, NEW.flagged_for_review
            );
        END IF;
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_screening_logs (
            screening_id, job_id, candidate_id, action_type,
            old_overall_score, new_overall_score,
            old_flagged, new_flagged
        ) VALUES (
            OLD.id, OLD.job_id, OLD.candidate_id, 'DELETE',
            OLD.overall_score, NULL,
            OLD.flagged_for_review, NULL
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_screening ON screening_results;
CREATE TRIGGER trg_audit_screening
    AFTER INSERT OR UPDATE OR DELETE ON screening_results
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_screening_changes();

-- -----------------------------------------------------------------------------
-- 4. User-Defined Function: Compute Candidate Total Experience from Normalized Table
-- Calculates cumulative tenure relationally from candidate_experiences.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calculate_candidate_experience_tenure(p_candidate_id VARCHAR)
RETURNS NUMERIC AS $$
DECLARE
    v_total_years NUMERIC;
BEGIN
    SELECT COALESCE(SUM(years), 0.0)
    INTO v_total_years
    FROM candidate_experiences
    WHERE candidate_id = p_candidate_id;

    RETURN ROUND(v_total_years, 1);
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------------------------------
-- 5. Stored Procedure: Batch Recalculate Hybrid Scores with ACID Transaction
-- Demonstrates explicit procedural transactions, constraint validation,
-- and atomic score recalculation directly inside the database engine.
-- -----------------------------------------------------------------------------
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
    v_weight_sum NUMERIC;
    v_updated_count INTEGER := 0;
BEGIN
    -- Validate scoring weight sum equals 1.0 (with small floating tolerance)
    v_weight_sum := p_w_semantic + p_w_req + p_w_pref + p_w_exp;
    IF v_weight_sum < 0.99 OR v_weight_sum > 1.01 THEN
        RAISE EXCEPTION 'Weights must sum to 1.0! Current sum: %', v_weight_sum;
    END IF;

    -- Verify job existence
    IF NOT EXISTS (SELECT 1 FROM jobs WHERE id = p_job_id) THEN
        RAISE EXCEPTION 'Job ID % does not exist in jobs table!', p_job_id;
    END IF;

    -- Atomic batch recalculation
    UPDATE screening_results
    SET overall_score = ROUND(
        LEAST(100.0, GREATEST(0.0,
            (p_w_semantic * semantic_score) +
            (p_w_req * required_skill_score) +
            (p_w_pref * preferred_skill_score) +
            (p_w_exp * experience_score)
        ))::numeric, 2
    )
    WHERE job_id = p_job_id;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;
    RAISE NOTICE 'Successfully recalculated scores for % candidates for job %', v_updated_count, p_job_id;
END;
$$;
