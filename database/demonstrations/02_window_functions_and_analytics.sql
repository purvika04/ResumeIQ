-- =============================================================================
-- ResumeIQ DBMS Demonstration 02: Window Functions & Advanced Analytics
-- Academic Demonstration Script for Viva Defense
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 2.1: Multi-metric Window Rankings (RANK, DENSE_RANK, PERCENT_RANK)'
\echo 'Evaluating candidate relative standing within their specific job cohort'
\echo '----------------------------------------------------------------------'

SELECT 
    j.title AS job_title,
    c.name AS candidate_name,
    sr.overall_score,
    RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC) AS rank_pos,
    DENSE_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC) AS dense_rank_pos,
    ROUND((PERCENT_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score) * 100)::numeric, 1) AS percentile_rank,
    NTILE(4) OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC) AS quartile_tier
FROM screening_results sr
JOIN jobs j ON sr.job_id = j.id
JOIN candidates c ON sr.candidate_id = c.id
WHERE j.title LIKE '%Python%' OR j.title LIKE '%Architect%'
ORDER BY j.title, rank_pos
LIMIT 10;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 2.2: Window Aggregates & Partition Comparisons'
\echo 'Candidate score vs job cohort min, max, avg, and running total'
\echo '----------------------------------------------------------------------'

SELECT 
    c.name AS candidate_name,
    sr.overall_score,
    ROUND(AVG(sr.overall_score) OVER (PARTITION BY sr.job_id)::numeric, 2) AS cohort_avg,
    ROUND(MAX(sr.overall_score) OVER (PARTITION BY sr.job_id)::numeric, 2) AS cohort_max,
    ROUND(MIN(sr.overall_score) OVER (PARTITION BY sr.job_id)::numeric, 2) AS cohort_min,
    ROUND((sr.overall_score - AVG(sr.overall_score) OVER (PARTITION BY sr.job_id))::numeric, 2) AS diff_from_avg,
    LAG(sr.overall_score, 1) OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC) AS score_above,
    LEAD(sr.overall_score, 1) OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC) AS score_below
FROM screening_results sr
JOIN candidates c ON sr.candidate_id = c.id
WHERE sr.job_id = (SELECT id FROM jobs WHERE title LIKE '%Python%' LIMIT 1)
ORDER BY sr.overall_score DESC
LIMIT 6;
