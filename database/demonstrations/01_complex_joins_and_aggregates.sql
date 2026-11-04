-- =============================================================================
-- ResumeIQ DBMS Demonstration 01: Complex Joins, Subqueries & Aggregations
-- Academic Demonstration Script for Viva Defense
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 1.1: Complex 5-Way Join with Left Outer Joins'
\echo 'Linking Candidates -> Education -> Experience -> Skills -> Screenings'
\echo '----------------------------------------------------------------------'

SELECT 
    c.id AS candidate_id,
    c.name AS candidate_name,
    c."current_role" AS current_designation,
    c.total_experience_years,
    COALESCE(ce.degree || ' in ' || COALESCE(ce.field_of_study, 'General'), 'No Degree') AS education_record,
    COALESCE(cx.title || ' at ' || cx.company, 'No Listed Experience') AS experience_record,
    COUNT(DISTINCT cs.skill_name) AS skill_count,
    ROUND(AVG(sr.overall_score)::numeric, 1) AS avg_screening_score
FROM candidates c
LEFT JOIN candidate_educations ce ON c.id = ce.candidate_id
LEFT JOIN candidate_experiences cx ON c.id = cx.candidate_id
LEFT JOIN candidate_skills cs ON c.id = cs.candidate_id
LEFT JOIN screening_results sr ON c.id = sr.candidate_id
GROUP BY c.id, c.name, c."current_role", c.total_experience_years, ce.degree, ce.field_of_study, cx.title, cx.company
ORDER BY avg_screening_score DESC NULLS LAST, c.name
LIMIT 5;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 1.2: Correlated & Nested Subqueries'
\echo 'Find candidates whose score strictly exceeds the cohort average for a job'
\echo '----------------------------------------------------------------------'

SELECT 
    sr.job_id,
    j.title AS job_title,
    c.name AS candidate_name,
    sr.overall_score,
    (
        SELECT ROUND(AVG(sr2.overall_score)::numeric, 2)
        FROM screening_results sr2
        WHERE sr2.job_id = sr.job_id
    ) AS cohort_mean_score,
    ROUND((sr.overall_score - (
        SELECT AVG(sr2.overall_score)
        FROM screening_results sr2
        WHERE sr2.job_id = sr.job_id
    ))::numeric, 2) AS points_above_cohort
FROM screening_results sr
JOIN candidates c ON sr.candidate_id = c.id
JOIN jobs j ON sr.job_id = j.id
WHERE sr.overall_score > (
    SELECT AVG(sr3.overall_score)
    FROM screening_results sr3
    WHERE sr3.job_id = sr.job_id
)
ORDER BY points_above_cohort DESC
LIMIT 5;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 1.3: Advanced Aggregations with HAVING and Conditional Aggregates'
\echo 'Recruitment Pipeline Job Summary: Pass rates, Tier distributions'
\echo '----------------------------------------------------------------------'

SELECT 
    j.title AS job_title,
    j.department,
    COUNT(sr.id) AS total_screened,
    COUNT(CASE WHEN sr.overall_score >= 70.0 THEN 1 END) AS high_match_candidates,
    COUNT(CASE WHEN sr.overall_score BETWEEN 40.0 AND 69.9 THEN 1 END) AS moderate_match_candidates,
    COUNT(CASE WHEN sr.overall_score < 40.0 THEN 1 END) AS low_match_candidates,
    ROUND(AVG(sr.overall_score)::numeric, 2) AS avg_job_score,
    ROUND(STDDEV(sr.overall_score)::numeric, 2) AS score_std_deviation
FROM jobs j
JOIN screening_results sr ON j.id = sr.job_id
GROUP BY j.id, j.title, j.department
HAVING COUNT(sr.id) >= 5
ORDER BY avg_job_score DESC;
