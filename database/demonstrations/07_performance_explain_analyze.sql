-- =============================================================================
-- ResumeIQ DBMS Demonstration 07: Query Optimization & EXPLAIN ANALYZE
-- Academic Demonstration Script for Viva Defense & Performance Analysis
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 7.1: High-Frequency Candidate Search: Functional Index on LOWER(email)'
\echo 'Index: idx_candidates_lower_email'
\echo '----------------------------------------------------------------------'

EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE)
SELECT id, name, email, "current_role"
FROM candidates
WHERE LOWER(email) = 'alex.morgan.dev@gmail.com';

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 7.2: Ranking & Filtering: Composite Index on (job_id, overall_score DESC)'
\echo 'Index: idx_screening_job_score_desc'
\echo '----------------------------------------------------------------------'

EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE)
SELECT candidate_id, overall_score, semantic_score, required_skill_score
FROM screening_results
WHERE job_id = 'job-cloud-devops-engineer'
ORDER BY overall_score DESC
LIMIT 5;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 7.3: Exception Review Queue: Partial Filtered Index on flagged_for_review'
\echo 'Index: idx_screening_flagged_for_review WHERE flagged_for_review = TRUE'
\echo '----------------------------------------------------------------------'

EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE)
SELECT id, candidate_id, overall_score, flag_reason
FROM screening_results
WHERE flagged_for_review = TRUE;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 7.4: Covering Index (Index-Only Scan) with INCLUDE clause'
\echo 'Index: idx_cand_skills_covering (candidate_id) INCLUDE (skill_name, category, proficiency)'
\echo '----------------------------------------------------------------------'

EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE)
SELECT candidate_id, skill_name, category, proficiency
FROM candidate_skills
WHERE candidate_id = 'alex_morgan';

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 7.5: Complex Analytical View Execution Plan'
\echo 'View: v_candidate_rankings_dense'
\echo '----------------------------------------------------------------------'

EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT job_title, candidate_name, overall_score, rank_position, percentile_ranking
FROM v_candidate_rankings_dense
WHERE job_id = 'job-cloud-devops-engineer'
ORDER BY rank_position
LIMIT 5;
