-- =============================================================================
-- ResumeIQ — Analytical, Reporting & Window Function Database Views
-- DBMS Target: PostgreSQL 18+
-- File: 01_analytical_and_reporting_views.sql
-- Concepts Demonstrated: Relational Views, Window Functions (DENSE_RANK,
-- PERCENT_RANK, AVG OVER), Multi-Table JOINs, Aggregations (STRING_AGG, COUNT, AVG)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- View 1: v_candidate_rankings_dense
-- Computes deterministic ranks, percentiles, and job average deltas dynamically
-- using standard SQL Window Functions.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_candidate_rankings_dense AS
SELECT
    DENSE_RANK() OVER (
        PARTITION BY sr.job_id 
        ORDER BY sr.overall_score DESC, sr.semantic_score DESC
    ) AS rank_position,
    ROUND(
        (PERCENT_RANK() OVER (
            PARTITION BY sr.job_id 
            ORDER BY sr.overall_score ASC
        ) * 100.0)::numeric, 1
    ) AS percentile_ranking,
    j.id AS job_id,
    j.title AS job_title,
    j.department AS job_department,
    c.id AS candidate_id,
    c.name AS candidate_name,
    c.email AS candidate_email,
    c.current_role,
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
    sr.created_at AS screened_at
FROM screening_results sr
JOIN jobs j ON sr.job_id = j.id
JOIN candidates c ON sr.candidate_id = c.id;

-- -----------------------------------------------------------------------------
-- View 2: v_skill_gap_matrix
-- Evaluates candidate skill compliance against mandatory core competencies.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_skill_gap_matrix AS
SELECT
    j.id AS job_id,
    j.title AS job_title,
    c.id AS candidate_id,
    c.name AS candidate_name,
    COUNT(DISTINCT js.skill_name) AS total_required_skills,
    COUNT(DISTINCT cs.skill_name) AS matched_skills_count,
    ROUND(
        (COUNT(DISTINCT cs.skill_name)::numeric / NULLIF(COUNT(DISTINCT js.skill_name), 0) * 100.0)::numeric, 1
    ) AS skill_coverage_pct,
    COALESCE(STRING_AGG(DISTINCT cs.skill_name, ', ' ORDER BY cs.skill_name), 'None') AS matched_skills_list
FROM jobs j
CROSS JOIN candidates c
LEFT JOIN job_skills js ON j.id = js.job_id AND js.is_required = TRUE
LEFT JOIN candidate_skills cs ON c.id = cs.candidate_id AND LOWER(TRIM(cs.skill_name)) = LOWER(TRIM(js.skill_name))
GROUP BY j.id, j.title, c.id, c.name;

-- -----------------------------------------------------------------------------
-- View 3: v_recruitment_funnel_summary
-- Executive dashboard aggregation summarizing applicants, scores, and reviews.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_recruitment_funnel_summary AS
SELECT
    j.id AS job_id,
    j.title AS job_title,
    j.department,
    j.status AS job_status,
    COUNT(sr.id) AS total_candidates_screened,
    ROUND(COALESCE(AVG(sr.overall_score), 0.0)::numeric, 2) AS mean_score,
    ROUND(COALESCE(MAX(sr.overall_score), 0.0)::numeric, 2) AS top_score,
    ROUND(COALESCE(MIN(sr.overall_score), 0.0)::numeric, 2) AS lowest_score,
    SUM(CASE WHEN sr.overall_score >= 80.0 THEN 1 ELSE 0 END) AS top_tier_candidates,
    SUM(CASE WHEN sr.overall_score >= 60.0 AND sr.overall_score < 80.0 THEN 1 ELSE 0 END) AS mid_tier_candidates,
    SUM(CASE WHEN sr.overall_score < 60.0 THEN 1 ELSE 0 END) AS low_tier_candidates,
    SUM(CASE WHEN sr.flagged_for_review = TRUE THEN 1 ELSE 0 END) AS flagged_for_manual_review,
    COUNT(DISTINCT a.id) AS formal_applications_count,
    COUNT(DISTINCT i.id) AS scheduled_interviews_count
FROM jobs j
LEFT JOIN screening_results sr ON j.id = sr.job_id
LEFT JOIN applications a ON j.id = a.job_id
LEFT JOIN interviews i ON a.id = i.application_id
GROUP BY j.id, j.title, j.department, j.status;

-- -----------------------------------------------------------------------------
-- View 4: v_candidate_comprehensive_profile
-- Relational 3NF denormalized view joining personal info, degrees, and skills.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_candidate_comprehensive_profile AS
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
