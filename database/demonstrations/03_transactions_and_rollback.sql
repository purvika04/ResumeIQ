-- =============================================================================
-- ResumeIQ DBMS Demonstration 03: Transactions, ACID & Rollback
-- Academic Demonstration Script for Viva Defense
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 3.1: Full Transaction Rollback on Integrity Violation (Atomicity)'
\echo 'Attempting multi-table atomic insert where the second step fails'
\echo '----------------------------------------------------------------------'

-- Initial count
SELECT COUNT(*) AS candidates_before FROM candidates WHERE email = 'transaction.test@resumeiq.ai';

BEGIN;

INSERT INTO candidates (id, name, email, "current_role")
VALUES ('cand-tx-atomic-test', 'Transaction Test Candidate', 'transaction.test@resumeiq.ai', 'Software Engineer');

-- Deliberately trigger an error (score > 100 violates chk_sr_overall)
INSERT INTO screening_results (id, job_id, candidate_id, overall_score, semantic_score, required_skill_score, preferred_skill_score, experience_score)
VALUES ('screen-tx-bad', (SELECT id FROM jobs LIMIT 1), 'cand-tx-atomic-test', 125.0, 90.0, 90.0, 90.0, 90.0);

-- If error occurred, PostgreSQL automatically aborts the transaction block.
-- Demonstrating ROLLBACK:
ROLLBACK;

-- Verify atomicity: The candidate record was NOT committed
SELECT COUNT(*) AS candidates_after_abort FROM candidates WHERE email = 'transaction.test@resumeiq.ai';

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 3.2: Partial Rollback Using SAVEPOINT (Selective Recovery)'
\echo 'Preserve step 1 while cleanly rolling back step 2'
\echo '----------------------------------------------------------------------'

BEGIN;

-- Step 1: Insert valid candidate
INSERT INTO candidates (id, name, email, "current_role")
VALUES ('cand-tx-savepoint', 'Savepoint Candidate', 'savepoint.test@resumeiq.ai', 'Platform Specialist');

SAVEPOINT candidate_created;

-- Step 2: Attempt an invalid operation in a nested block
-- In raw psql, if an unhandled error happens, the transaction must rollback or use an internal block.
-- Let us use a PL/pgSQL block to demonstrate controlled exception handling with SAVEPOINT:
DO \$\$
BEGIN
    INSERT INTO screening_results (id, job_id, candidate_id, overall_score, semantic_score, required_skill_score, preferred_skill_score, experience_score)
    VALUES ('screen-tx-sp-bad', (SELECT id FROM jobs LIMIT 1), 'cand-tx-savepoint', -10.0, 50.0, 50.0, 50.0, 50.0);
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'Caught check_violation as expected! Rolling back to savepoint candidate_created.';
END \$\$;

-- Step 3: Add education record for candidate
INSERT INTO candidate_educations (id, candidate_id, degree, institution, graduation_year)
VALUES ('edu-tx-sp', 'cand-tx-savepoint', 'Master of Science', 'Technical University', 2024);

COMMIT;

-- Verify: Candidate and education are committed, bad screening was rejected
SELECT c.name, c.email, ce.degree, ce.institution
FROM candidates c
JOIN candidate_educations ce ON c.id = ce.candidate_id
WHERE c.id = 'cand-tx-savepoint';

-- Clean up test records
DELETE FROM candidate_educations WHERE id = 'edu-tx-sp';
DELETE FROM candidates WHERE id = 'cand-tx-savepoint';
