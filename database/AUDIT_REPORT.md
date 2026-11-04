# ResumeIQ — Comprehensive DBMS Implementation Audit Report

**Auditor:** Database Architecture & Engineering Team  
**System:** ResumeIQ Recruitment Platform  
**Target Database:** PostgreSQL 18.6 (Apple Silicon Local Instance)  
**Legacy/Preserved Store:** SQLite 3 (`backend/data/resumeiq.db`)

---

## 1. Executive Summary

This audit assesses the data architecture of **ResumeIQ** before transitioning from local SQLite storage to **PostgreSQL 18** as the primary relational DBMS. The goal is to strengthen relational database concepts (normalization, integrity constraints, triggers, views, indexing, transactions) while maintaining 100% backward compatibility and zero downtime for existing backend APIs and the React frontend.

---

## 2. Current Architecture & Findings

### 2.1 Storage Layer Configuration
- **Relational Store**: SQLAlchemy 2.0 ORM configured with dynamic connection handling via `DATABASE_URL`.
- **Document Store**: Dual-mode MongoDB / Local Atomic JSON Store handling unstructured resume text and NLP model telemetry.
- **Current Relational Tables**:
  - `recruiters` (1 record)
  - `candidates` (15 records)
  - `jobs` (5 records)
  - `candidate_skills` (88 records)
  - `job_skills` (10 records)
  - `applications` (0 records)
  - `screening_results` (66 records)
  - `interviews` (0 records)

### 2.2 Relational Normalization Audit (1NF, 2NF, 3NF)
| Table | Current State | Normalization Assessment | Action Required |
|---|---|---|---|
| `candidates` | Stores `education_json` as serialized JSON text | **1NF Violation**: Non-atomic multi-valued repeating group. | Normalize into dedicated `candidate_educations` relational table with FK to `candidates.id`. Retain `education_json` for frontend payload compatibility. |
| `candidates` | Stores work history summary only; detailed job roles kept in document store | **Under-normalized**: Work experience items are not relationally queryable. | Create `candidate_experiences` relational table for relational timeline filtering and tenure queries. |
| `jobs` | Stores `required_skills_json` & `preferred_skills_json` alongside `job_skills` junction table | **Dual Representation**: Junction table `job_skills` already exists; JSON text acts as denormalized cache. | Enforce synchronization so `job_skills` represents source of truth with composite uniqueness. |
| `skills` | Table exists with `id`, `name`, `category`, `aliases_json` | **3NF Compliant**: Canonical skill dictionary with category classification. | Pre-populate with comprehensive engineering taxonomy (70+ core competencies). |
| `candidate_skills` | Junction table `(candidate_id, skill_id, skill_name, category)` | **3NF Compliant** | Add composite unique constraint `UNIQUE(candidate_id, skill_name)` to prevent duplicate skill records per candidate. |
| `job_skills` | Junction table `(job_id, skill_id, skill_name, is_required)` | **3NF Compliant** | Add composite unique constraint `UNIQUE(job_id, skill_name)`. |
| `screening_results` | Results table linking `job_id` and `candidate_id` | **3NF Compliant** | Enforce composite `UNIQUE(job_id, candidate_id)` and check constraints on scores ($0 \le \text{score} \le 100$). |

---

## 3. Database Constraints & Integrity Plan

1. **Domain & Check Constraints**:
   - `screening_results.overall_score`: `CHECK (overall_score >= 0.0 AND overall_score <= 100.0)`
   - `screening_results.semantic_score`: `CHECK (semantic_score >= 0.0 AND semantic_score <= 100.0)`
   - `screening_results.required_skill_score`: `CHECK (required_skill_score >= 0.0 AND required_skill_score <= 100.0)`
   - `screening_results.preferred_skill_score`: `CHECK (preferred_skill_score >= 0.0 AND preferred_skill_score <= 100.0)`
   - `screening_results.experience_score`: `CHECK (experience_score >= 0.0 AND experience_score <= 100.0)`
   - `applications.status`: `CHECK (status IN ('submitted', 'screening', 'shortlisted', 'rejected', 'hired'))`
   - `interviews.status`: `CHECK (status IN ('scheduled', 'completed', 'cancelled'))`
   - `interviews.rating`: `CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5))`

2. **Foreign Key Integrity**:
   - All child tables (`candidate_skills`, `candidate_educations`, `candidate_experiences`, `job_skills`, `applications`, `screening_results`) declare `ON DELETE CASCADE`.

3. **Composite & Unique Keys**:
   - `candidates.email`: `UNIQUE`
   - `skills.name`: `UNIQUE`
   - `candidate_skills`: `UNIQUE(candidate_id, skill_name)`
   - `job_skills`: `UNIQUE(job_id, skill_name)`
   - `screening_results`: `UNIQUE(job_id, candidate_id)`
   - `applications`: `UNIQUE(candidate_id, job_id)`

4. **Performance & Indexing**:
   - B-tree index on `candidates(email)` and functional index on `LOWER(email)`.
   - Covering composite index on `screening_results(job_id, overall_score DESC)`.
   - Foreign key indexes on all child entity lookup columns.

---

## 4. PostgreSQL 18 Migration Roadmap

1. **Driver Setup**: Installed `psycopg[binary]` (Psycopg 3) and `psycopg2-binary` in Python 3.11 virtual environment.
2. **Target Schema Creation**: Execute PostgreSQL DDL incorporating normalized tables (`candidate_educations`, `candidate_experiences`) and constraint definitions.
3. **Data Migration**: Read all rows from preserved SQLite database (`resumeiq.db`) and write transactionally into PostgreSQL 18 without loss.
4. **Application Switchover**: Update environment configuration to `postgresql://apple@localhost:5432/resumeiq` and restart backend.
5. **Advanced DBMS SQL Suite**: Create modular SQL scripts for views, triggers, stored procedures, audit logging, and RBAC in `resumeiq/database/`.
