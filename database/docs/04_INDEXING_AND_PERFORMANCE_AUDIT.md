# ResumeIQ: Indexing Architecture & Query Performance Audit

This document details the **35 indexes** established in the ResumeIQ PostgreSQL 18 database, comparing execution plans before and after indexing using real `EXPLAIN (ANALYZE, BUFFERS)` benchmarks.

---

## 1. Index Classification Summary

| Index Classification | Strategy & Clause | Benchmark Target Query | Physical Index Name |
|---|---|---|---|
| **B-Tree Primary Key** | Unique B-Tree | Exact Entity Lookup by ID | `candidates_pkey`, `jobs_pkey`, etc. |
| **Functional Index** | Expression B-Tree `LOWER(email)` | Case-insensitive Candidate Login & Verification | `idx_candidates_lower_email` |
| **Composite B-Tree** | `(job_id, overall_score DESC)` | High-throughput Candidate Ranking Tables | `idx_screening_job_score_desc` |
| **Partial / Filtered** | `WHERE flagged_for_review = TRUE` | Recruiter Exception Review Queue | `idx_screening_flagged_for_review` |
| **Covering Index** | `INCLUDE (skill_name, category, ...)` | Skill Inventory Queries (Index-Only Scan) | `idx_cand_skills_covering` |
| **Filtered Temporal** | `WHERE status = 'active'` | Active Job Postings Search | `idx_active_jobs_created` |

---

## 2. Real Query Plan Measurements (`EXPLAIN ANALYZE, BUFFERS`)

> [!NOTE]
> **Academic Benchmark Context & Scale Distinction**:
> The execution times below are **empirically measured on the current development dataset** (16 candidates, 8 jobs, 130 screening results). In a small dataset residing entirely in memory buffers (`shared hit=2`), execution times for both sequential scans and index scans are in the microsecond range ($0.02\text{--}0.50\text{ ms}$).
> The mathematical rationale for indexing is demonstrated by asymptotic computational complexity: at production scale ($100,000+$ resumes), sequential scans degrade linearly $O(N)$ causing severe disk I/O thrashing, whereas B-Tree indexes maintain $O(\log N)$ logarithmic bounds.

### Benchmark 1: Case-Insensitive Email Search (`idx_candidates_lower_email`)

#### Query:
```sql
SELECT id, name, email, "current_role"
FROM candidates
WHERE LOWER(email) = 'alex.morgan.dev@gmail.com';
```

#### Without Index / Sequential Table Scan:
```text
Seq Scan on candidates  (cost=0.00..1.20 rows=1 width=236) (actual time=0.042..0.048 rows=1 loops=1)
  Filter: (lower((email)::text) = 'alex.morgan.dev@gmail.com'::text)
  Rows Removed by Filter: 15
  Buffers: shared hit=1
Execution Time: 0.068 ms
```

#### With Functional Index (`idx_candidates_lower_email`):
```text
Index Scan using idx_candidates_lower_email on candidates  (cost=0.14..8.16 rows=1 width=236) (actual time=0.024..0.026 rows=1 loops=1)
  Index Cond: (lower((email)::text) = 'alex.morgan.dev@gmail.com'::text)
  Buffers: shared hit=2
Execution Time: 0.038 ms
```

#### Empirical Analysis & Large-Scale Theoretical Projection:
1. **Empirical Observation (Current Dataset, 16 rows):**
   - The query executes in **0.038 ms** with the index vs **0.068 ms** without it. Both hit in-memory shared buffers (`shared hit`).
2. **Theoretical Asymptotic Behavior at Large Scale ($100,000+$ rows):**
   - **Without Index ($O(N)$):** The database engine must perform a full table scan across thousands of 8 KB disk pages, executing the CPU-bound `lower()` function on every string in every row. If each disk block holds 30 rows, scanning 100,000 candidates requires reading ~3,333 disk pages ($> 26\text{ MB}$ of I/O).
   - **With Functional B-Tree ($O(\log N)$):** For 100,000 candidates with a branching factor of ~300 in the B-Tree, the search depth is only $\approx 3$ page reads ($\log_{300}(100000) \approx 2.03$), guaranteeing sub-millisecond retrieval regardless of table growth.

---

### Benchmark 2: Covering Index with `INCLUDE` (`idx_cand_skills_covering`)

#### Query:
```sql
SELECT candidate_id, skill_name, category, proficiency
FROM candidate_skills
WHERE candidate_id = 'alex_morgan';
```

#### Execution Plan:
```text
Index Only Scan using idx_cand_skills_covering on candidate_skills  (cost=0.14..8.16 rows=12 width=48) (actual time=0.021..0.023 rows=12 loops=1)
  Index Cond: (candidate_id = 'alex_morgan'::text)
  Heap Fetches: 0
  Buffers: shared hit=2
Planning Time: 0.436 ms
Execution Time: 0.027 ms
```
- **Performance Interpretation:** Notice `Heap Fetches: 0`. The database engine satisfies the entire query directly from the leaf nodes of the B-Tree index without reading table pages from disk (Zero Heap Access). This eliminates disk I/O bottlenecks.

---

### Benchmark 3: Multi-metric Window Aggregation View (`v_candidate_rankings_dense`)

#### Query:
```sql
SELECT job_title, candidate_name, overall_score, rank_position, percentile_ranking
FROM v_candidate_rankings_dense
WHERE job_id = 'job-cloud-devops-engineer'
ORDER BY rank_position
LIMIT 5;
```

#### Execution Plan:
```text
Limit  (cost=24.65..24.65 rows=1 width=114) (actual time=0.341..0.351 rows=5 loops=1)
  Buffers: shared hit=18
  ->  Sort (actual time=0.340..0.341 rows=5 loops=1)
        Sort Key: v_candidate_rankings_dense.rank_position
        Sort Method: top-N heapsort  Memory: 26kB
        ->  WindowAgg (actual time=0.196..0.324 rows=66 loops=1)
              Window: w2 AS (PARTITION BY sr.job_id ORDER BY sr.overall_score)
Planning Time: 0.624 ms
Execution Time: 0.414 ms
```
- **Performance Interpretation:** Top-N heapsort executes in **0.414 ms** total time using only 26 kB of memory, demonstrating query efficiency across multi-table window partitions.
