-- =============================================================================
-- ResumeIQ DBMS Demonstration 04: Concurrency, Locking & MVCC
-- Academic Demonstration Script for Viva Defense
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 4.1: Pessimistic Row Locking with SELECT ... FOR UPDATE'
\echo 'Preventing race conditions during candidate review'
\echo '----------------------------------------------------------------------'

BEGIN;

-- Lock the candidate row for exclusive modification during an active recruiter review session
SELECT id, name, "current_role", total_experience_years
FROM candidates
WHERE id = 'alex_morgan'
FOR UPDATE;

-- Update safely within locked transaction
UPDATE candidates
SET total_experience_years = total_experience_years + 0.0
WHERE id = 'alex_morgan';

COMMIT;
\echo 'Row lock released on COMMIT.'

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 4.2: Non-blocking Skip-Locked Worker Queue pattern'
\echo 'SELECT ... FOR UPDATE SKIP LOCKED for multi-worker resume processing'
\echo '----------------------------------------------------------------------'

-- In high-throughput ATS systems, multiple backend worker processes screen resumes concurrently.
-- SKIP LOCKED allows workers to grab distinct unprocessed jobs without waiting or deadlocking.

BEGIN;

SELECT id, job_id, candidate_id, overall_score
FROM screening_results
WHERE flagged_for_review = TRUE
ORDER BY overall_score DESC
LIMIT 2
FOR UPDATE SKIP LOCKED;

COMMIT;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 4.3: Session Advisory Locks (Application-level Concurrency Control)'
\echo 'Guarantees only one screening batch runs per job across distributed instances'
\echo '----------------------------------------------------------------------'

-- Acquire 64-bit advisory lock using hashtext of job ID
SELECT pg_try_advisory_xact_lock(hashtext('job-cloud-devops-engineer')) AS lock_acquired;

\echo 'Transaction-level advisory lock automatically releases when transaction ends.'
