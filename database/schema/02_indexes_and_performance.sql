-- =============================================================================
-- ResumeIQ — Advanced Indexing & Query Performance Optimization
-- DBMS Target: PostgreSQL 18+
-- File: 02_indexes_and_performance.sql
-- Concepts Demonstrated: B-tree, Functional/Expression Indexes, Composite Indexes,
-- Partial/Filtered Indexes, Covering Indexes (Index-Only Scans), EXPLAIN ANALYZE
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Functional / Expression Index
-- Enables index-backed lookups regardless of email case:
-- SELECT * FROM candidates WHERE LOWER(email) = LOWER('user@example.com');
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_candidates_lower_email
    ON candidates (LOWER(email));

-- -----------------------------------------------------------------------------
-- 2. Foreign Key Indexes (Eliminates Seq Scans during JOIN operations)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cand_educations_candidate_id
    ON candidate_educations (candidate_id);

CREATE INDEX IF NOT EXISTS idx_cand_experiences_candidate_id
    ON candidate_experiences (candidate_id);

CREATE INDEX IF NOT EXISTS idx_cand_skills_candidate_id
    ON candidate_skills (candidate_id);

CREATE INDEX IF NOT EXISTS idx_cand_skills_skill_id
    ON candidate_skills (skill_id);

CREATE INDEX IF NOT EXISTS idx_job_skills_job_id
    ON job_skills (job_id);

CREATE INDEX IF NOT EXISTS idx_job_skills_skill_id
    ON job_skills (skill_id);

CREATE INDEX IF NOT EXISTS idx_applications_candidate_id
    ON applications (candidate_id);

CREATE INDEX IF NOT EXISTS idx_applications_job_id
    ON applications (job_id);

CREATE INDEX IF NOT EXISTS idx_interviews_application_id
    ON interviews (application_id);

-- -----------------------------------------------------------------------------
-- 3. Composite Multi-Column Ranking Index with Sort Direction
-- Accelerates the primary recruiter ranking query:
-- SELECT * FROM screening_results WHERE job_id = ? ORDER BY overall_score DESC;
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_screening_job_score_desc
    ON screening_results (job_id, overall_score DESC);

-- -----------------------------------------------------------------------------
-- 4. Partial / Filtered Index
-- Only indexes currently open job postings. Saves buffer cache and maintenance
-- overhead compared to indexing all archived/draft historical jobs.
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_active_jobs_created
    ON jobs (created_at DESC)
    WHERE status = 'active';

-- Partial index for flagged screenings requiring recruiter human-in-the-loop audit
CREATE INDEX IF NOT EXISTS idx_screening_flagged_for_review
    ON screening_results (job_id, overall_score DESC)
    WHERE flagged_for_review = TRUE;

-- -----------------------------------------------------------------------------
-- 5. Covering Index with INCLUDE Clause (PostgreSQL Index-Only Scans)
-- Satisfies skill list lookups directly from the index leaf pages without
-- visiting the table heap.
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cand_skills_covering
    ON candidate_skills (candidate_id)
    INCLUDE (skill_name, category, proficiency);

-- -----------------------------------------------------------------------------
-- 6. Performance Verification & Statistics
-- Refresh query planner distribution statistics
-- -----------------------------------------------------------------------------
ANALYZE candidates;
ANALYZE jobs;
ANALYZE candidate_skills;
ANALYZE job_skills;
ANALYZE screening_results;
