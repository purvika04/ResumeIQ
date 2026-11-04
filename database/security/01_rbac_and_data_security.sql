-- =============================================================================
-- ResumeIQ — Role-Based Access Control (RBAC) & Database Security
-- DBMS Target: PostgreSQL 18+
-- File: 01_rbac_and_data_security.sql
-- Concepts Demonstrated: Database Roles, Principle of Least Privilege, GRANT/REVOKE,
-- Row-Level Security (RLS), Data Masking & Auditing
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Create Functional Database Roles
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    -- Application Backend Role (Used by FastAPI backend connection pool)
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'resumeiq_app') THEN
        CREATE ROLE resumeiq_app WITH LOGIN PASSWORD 'app_secure_password';
    END IF;

    -- Business Intelligence / Analyst Role (Read-only on analytical views)
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'resumeiq_analyst') THEN
        CREATE ROLE resumeiq_analyst WITH LOGIN PASSWORD 'analyst_secure_password';
    END IF;

    -- Compliance & Audit Reviewer Role (Read-only on audit logs & screening records)
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'resumeiq_auditor') THEN
        CREATE ROLE resumeiq_auditor WITH LOGIN PASSWORD 'auditor_secure_password';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 2. Principle of Least Privilege: Application Role Grants
-- The backend role requires CRUD on operational entities, but no DROP/ALTER rights.
-- -----------------------------------------------------------------------------
GRANT CONNECT ON DATABASE resumeiq TO resumeiq_app;
GRANT USAGE ON SCHEMA public TO resumeiq_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO resumeiq_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO resumeiq_app;

-- -----------------------------------------------------------------------------
-- 3. Analyst Role Grants (Strictly Read-Only on Analytical Views & Tables)
-- -----------------------------------------------------------------------------
GRANT CONNECT ON DATABASE resumeiq TO resumeiq_analyst;
GRANT USAGE ON SCHEMA public TO resumeiq_analyst;

GRANT SELECT ON v_candidate_rankings_dense TO resumeiq_analyst;
GRANT SELECT ON v_skill_gap_matrix TO resumeiq_analyst;
GRANT SELECT ON v_recruitment_funnel_summary TO resumeiq_analyst;
GRANT SELECT ON v_candidate_comprehensive_profile TO resumeiq_analyst;
GRANT SELECT ON jobs, skills, screening_results TO resumeiq_analyst;

-- -----------------------------------------------------------------------------
-- 4. Auditor Role Grants (Compliance & Audit Verification)
-- -----------------------------------------------------------------------------
GRANT CONNECT ON DATABASE resumeiq TO resumeiq_auditor;
GRANT USAGE ON SCHEMA public TO resumeiq_auditor;

GRANT SELECT ON audit_screening_logs TO resumeiq_auditor;
GRANT SELECT ON screening_results TO resumeiq_auditor;
GRANT SELECT ON applications, interviews TO resumeiq_auditor;

-- -----------------------------------------------------------------------------
-- 5. Row-Level Security (RLS) Policy Demonstration
-- -----------------------------------------------------------------------------
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Default policy: Allow authenticated recruiters to read all jobs
DROP POLICY IF EXISTS p_read_all_jobs ON jobs;
CREATE POLICY p_read_all_jobs ON jobs
    FOR SELECT
    TO PUBLIC
    USING (true);

-- Allow recruiters to update only jobs they created or if admin
DROP POLICY IF EXISTS p_modify_own_jobs ON jobs;
CREATE POLICY p_modify_own_jobs ON jobs
    FOR UPDATE
    TO PUBLIC
    USING (created_by IS NULL OR created_by = CURRENT_USER OR CURRENT_USER = 'apple');
