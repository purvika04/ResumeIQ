# ResumeIQ: Database Constraints & Integrity Verification

This document provides a detailed catalog of all **81 database constraints** verified in PostgreSQL 18 system catalog `pg_constraint` for the `public` schema.

---

## 1. Constraint Breakdown by Class

| Category | Catalog Identifier (`contype`) | Exact Count | Description |
|---|---|---|---|
| **NOT NULL Constraints** | `'n'` | **42** | Enforce data presence on all primary keys, required foreign keys, scores, and names. |
| **PRIMARY KEY Constraints** | `'p'` | **12** | Enforce entity uniqueness across all 12 tables. |
| **FOREIGN KEY Constraints** | `'f'` | **12** | Enforce referential integrity and define cascading delete behaviors. |
| **Domain CHECK Constraints** | `'c'` | **8** | Enforce numerical bounds and allowable state transitions. |
| **UNIQUE Constraints** | `'u'` | **7** | Enforce uniqueness on candidate emails, skill names, and composite pairs. |
| **TOTAL** | | **81** | Total constraints verified in `pg_constraint`. |

---

## 2. Domain CHECK Constraints (`contype = 'c'`)

1. **`chk_sr_overall` on `screening_results`:**
   $$\text{CHECK } (\text{overall\_score} \ge 0.0 \text{ AND } \text{overall\_score} \le 100.0)$$
2. **`chk_sr_semantic` on `screening_results`:**
   $$\text{CHECK } (\text{semantic\_score} \ge 0.0 \text{ AND } \text{semantic\_score} \le 100.0)$$
3. **`chk_sr_req_skill` on `screening_results`:**
   $$\text{CHECK } (\text{required\_skill\_score} \ge 0.0 \text{ AND } \text{required\_skill\_score} \le 100.0)$$
4. **`chk_sr_pref_skill` on `screening_results`:**
   $$\text{CHECK } (\text{preferred\_skill\_score} \ge 0.0 \text{ AND } \text{preferred\_skill\_score} \le 100.0)$$
5. **`chk_sr_exp` on `screening_results`:**
   $$\text{CHECK } (\text{experience\_score} \ge 0.0 \text{ AND } \text{experience\_score} \le 100.0)$$
6. **`chk_app_status` on `applications`:**
   $$\text{CHECK } (\text{status} \in (\text{'submitted'}, \text{'screening'}, \text{'shortlisted'}, \text{'rejected'}, \text{'hired'}))$$
7. **`chk_int_status` on `interviews`:**
   $$\text{CHECK } (\text{status} \in (\text{'scheduled'}, \text{'completed'}, \text{'cancelled'}))$$
8. **`chk_int_rating` on `interviews`:**
   $$\text{CHECK } (\text{rating IS NULL OR } (\text{rating} \ge 1 \text{ AND } \text{rating} \le 5))$$

---

## 3. Foreign Key Cascades & Referential Integrity (`contype = 'f'`)

| Constraint Name | Source Table | Source Column | Target Table | Target Column | On Delete Action |
|---|---|---|---|---|---|
| `applications_candidate_id_fkey` | `applications` | `candidate_id` | `candidates` | `id` | `CASCADE` |
| `applications_job_id_fkey` | `applications` | `job_id` | `jobs` | `id` | `CASCADE` |
| `candidate_educations_candidate_id_fkey` | `candidate_educations` | `candidate_id` | `candidates` | `id` | `CASCADE` |
| `candidate_experiences_candidate_id_fkey` | `candidate_experiences` | `candidate_id` | `candidates` | `id` | `CASCADE` |
| `candidate_skills_candidate_id_fkey` | `candidate_skills` | `candidate_id` | `candidates` | `id` | `CASCADE` |
| `candidate_skills_skill_id_fkey` | `candidate_skills` | `skill_id` | `skills` | `id` | `SET NULL` |
| `interviews_application_id_fkey` | `interviews` | `application_id` | `applications` | `id` | `CASCADE` |
| `job_skills_job_id_fkey` | `job_skills` | `job_id` | `jobs` | `id` | `CASCADE` |
| `job_skills_skill_id_fkey` | `job_skills` | `skill_id` | `skills` | `id` | `SET NULL` |
| `jobs_created_by_fkey` | `jobs` | `created_by` | `recruiters` | `id` | `SET NULL` |
| `screening_results_candidate_id_fkey` | `screening_results` | `candidate_id` | `candidates` | `id` | `CASCADE` |
| `screening_results_job_id_fkey` | `screening_results` | `job_id` | `jobs` | `id` | `CASCADE` |

---

## 4. Unique & Composite Constraints (`contype = 'u'`)

1. **`candidates_email_key`:** `UNIQUE (email)` on `candidates`
2. **`recruiters_email_key`:** `UNIQUE (email)` on `recruiters`
3. **`skills_name_key`:** `UNIQUE (name)` on `skills`
4. **`uq_cand_job`:** `UNIQUE (candidate_id, job_id)` on `applications`
5. **`uq_screen_job_cand`:** `UNIQUE (job_id, candidate_id)` on `screening_results`
6. **`uq_cand_skill_name`:** `UNIQUE (candidate_id, skill_name)` on `candidate_skills`
7. **`uq_job_skill_name`:** `UNIQUE (job_id, skill_name)` on `job_skills`
