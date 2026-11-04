# ResumeIQ: Views, Triggers, Stored Procedures & Security Guide

This document explains the advanced programmable database logic and security architectures implemented in ResumeIQ for presentation during a DBMS viva examination.

---

## 1. Analytical SQL Views & Window Functions

### 1. `v_candidate_rankings_dense`
- **Purpose:** Solves the hiring problem of tie-breaking and percentile calculation.
- **DBMS Mechanisms:**
  - `DENSE_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC, sr.semantic_score DESC)`: Assigns consecutive ranking positions without skipping numbers when candidates tie on score.
  - `PERCENT_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score)`: Calculates relative percentile ranking ($0.0\%$ to $100.0\%$).
  - `AVG(sr.overall_score) OVER (PARTITION BY sr.job_id)`: Cohort baseline score to calculate `delta_from_avg`.

### 2. `v_skill_gap_matrix`
- **Purpose:** Identifies exact candidate skill coverage against required job specifications.
- **DBMS Mechanisms:** `CROSS JOIN` between candidates and active jobs combined with `LEFT JOIN` on normalized `candidate_skills` to compute coverage percentages and aggregated skill lists.

### 3. `v_recruitment_funnel_summary`
- **Purpose:** Executive hiring dashboard.
- **DBMS Mechanisms:** Aggregate pipeline counts with `CASE` expressions grouping scores into Top-tier ($\ge 80\%$), Mid-tier ($60\text{--}79\%$), and Low-tier ($< 60\%$).

### 4. `v_candidate_comprehensive_profile`
- **Purpose:** 360-degree candidate portfolio.
- **DBMS Mechanisms:** Denormalizes `candidate_educations` and `candidate_skills` using PostgreSQL `STRING_AGG(DISTINCT ...)` into readable summaries.

---

## 2. Event-Driven Database Triggers

### `trg_audit_screening` (Audit Logging Trigger)
- **Fires on:** `AFTER INSERT OR UPDATE OR DELETE ON screening_results`
- **Target Table:** `audit_screening_logs`
- **Function:** `fn_audit_screening_changes()`
- **Academic Rationale:**
  In high-stakes recruitment and compliance-regulated environments, score modifications must have a non-repudiable audit trail. This trigger guarantees that every INSERT, score change, review flag toggle, or deletion is recorded with:
  - `old_overall_score` vs `new_overall_score`
  - `changed_by` (`CURRENT_USER`)
  - `changed_at` (`CURRENT_TIMESTAMP`)

---

## 3. Stored Procedures & Functions

### Stored Procedure: `sp_batch_recalculate_scores(p_job_id, ...)`
- **Language:** PL/pgSQL
- **Purpose:** In-database recalculation of candidate rankings when a recruiter adjusts component weights (e.g., boosting Semantic Similarity from 40% to 50%).
- **Academic Value:** Demonstrates running bulk analytical updates inside the database engine, avoiding network transmission of thousands of candidate rows to the application server and back.

### User-Defined Function: `fn_calculate_candidate_experience_tenure(p_candidate_id)`
- **Language:** PL/pgSQL
- **Purpose:** Computes verified total tenure from candidate employment records.

---

## 4. Transaction Management & ACID Guarantees

1. **Atomicity:** Ensured via `BEGIN`, `SAVEPOINT`, `ROLLBACK TO SAVEPOINT`, and `COMMIT`. When creating a candidate profile and screening score, if the screening insert violates a score constraint ($> 100$), the entire transaction is rolled back, preventing orphaned candidates.
2. **Consistency:** Enforced by 81 database constraints. Transactions that violate domain or referential rules cannot transition the database into an invalid state.
3. **Isolation:** PostgreSQL uses Multi-Version Concurrency Control (MVCC) with Read Committed default isolation. For critical operations, `SELECT ... FOR UPDATE` acquires row-level pessimistic locks to eliminate race conditions.
4. **Durability:** PostgreSQL Write-Ahead Logging (WAL) ensures committed transactions survive server restarts or power interruptions.

---

## 5. Security: RBAC & Row-Level Security (RLS)

1. **Role-Based Access Control (RBAC):**
   - `resumeiq_app`: Read/write access on domain tables; cannot modify audit tables.
   - `resumeiq_analyst`: Read-only access to analytical views and reporting summaries.
   - `resumeiq_auditor`: Read-only access to `audit_screening_logs`.
2. **Row-Level Security (RLS):**
   - Enabled on `jobs` table (`ALTER TABLE jobs ENABLE ROW LEVEL SECURITY`).
   - Policy `p_read_all_jobs`: Permissive read access for all recruiters.
   - Policy `p_modify_own_jobs`: Restricts update/delete privileges to the recruiter who created the job posting (`created_by = CURRENT_USER`).
