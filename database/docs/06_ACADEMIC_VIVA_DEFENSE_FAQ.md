# ResumeIQ: Academic DBMS Viva Defense Preparation & FAQ

This guide prepares an engineering student to defend the ResumeIQ database implementation during a viva examination.

---

## Top 15 Viva Questions & Model Answers

### Q1: What database system does ResumeIQ use, and what is its architecture?
> **Answer:** ResumeIQ utilizes **PostgreSQL 18** as its primary relational database running with connection pooling (10 pooled connections, max overflow 20). It employs a dual-database architecture: PostgreSQL manages structured relational data, constraints, foreign keys, and analytical views, while a document store manages raw resume texts and parsed JSON documents.

---

### Q2: How did you normalize the candidate education and experience data?
> **Answer:** Initially, educations and experiences were stored as embedded JSON arrays, which violated First Normal Form (1NF) due to non-atomic repeating groups. We normalized the schema by decomposing them into separate relational child tables: `candidate_educations` and `candidate_experiences`. Both tables reference `candidates(id)` via Foreign Keys with `ON DELETE CASCADE`.

---

### Q3: What is the difference between 3NF and BCNF, and does ResumeIQ satisfy BCNF?
> **Answer:** A relation is in 3NF if for every non-trivial functional dependency $X \to Y$, either $X$ is a superkey OR $Y$ is a prime attribute. BCNF is stricter: $X$ must *always* be a superkey. In ResumeIQ, all functional dependencies in core domain tables (`candidates`, `jobs`, `recruiters`, `screening_results`) originate strictly from candidate keys (`id`, `email`, or composite keys like `(job_id, candidate_id)`), satisfying BCNF.

---

### Q4: How do you prevent invalid scores from corrupting the screening system?
> **Answer:** We implemented database-level **CHECK constraints** (`chk_sr_overall`, `chk_sr_semantic`, `chk_sr_req_skill`, `chk_sr_pref_skill`, `chk_sr_exp`) enforcing that every score must satisfy $0.0 \le \text{score} \le 100.0$. Any attempt by the application layer or a direct SQL query to insert a negative score or a score $>100$ is rejected at the database engine level.

---

### Q5: What types of indexes did you implement beyond standard Primary Keys?
> **Answer:** We implemented **35 indexes** covering five specialized indexing strategies:
> 1. **Functional Indexes:** `idx_candidates_lower_email` indexing `LOWER(email)` for case-insensitive candidate searches.
> 2. **Composite Indexes:** `idx_screening_job_score_desc` on `(job_id, overall_score DESC)` for ranked candidate tables.
> 3. **Partial / Filtered Indexes:** `idx_screening_flagged_for_review` indexing only rows where `flagged_for_review = TRUE`, saving disk space and memory.
> 4. **Covering Indexes:** `idx_cand_skills_covering` using the `INCLUDE` clause to permit zero-heap-fetch **Index-Only Scans**.
> 5. **Filtered Temporal Indexes:** `idx_active_jobs_created` indexing active jobs by `created_at DESC`.

---

### Q6: What is a Covering Index, and how does it improve query performance?
> **Answer:** A covering index includes both the search keys and non-key payload columns (via the `INCLUDE` clause). In `idx_cand_skills_covering`, the index key is `candidate_id` while `INCLUDE` stores `(skill_name, category, proficiency)`. When querying a candidate's skills, PostgreSQL satisfies the query entirely from the B-Tree index pages with **0 Heap Fetches**, completely bypassing disk reads to the main table pages.

---

### Q7: Explain the window functions used in `v_candidate_rankings_dense`.
> **Answer:**
> - `DENSE_RANK() OVER (PARTITION BY sr.job_id ORDER BY sr.overall_score DESC, sr.semantic_score DESC)` generates consecutive ranking positions without skipping numbers when candidates tie.
> - `PERCENT_RANK()` computes relative percentile rank ($0.0\%$ to $100.0\%$).
> - `AVG(sr.overall_score) OVER (PARTITION BY sr.job_id)` dynamically calculates the cohort average for each job within the same query pass without requiring a self-join.

---

### Q8: How does your audit trigger work?
> **Answer:** We created trigger `trg_audit_screening` which fires `AFTER INSERT OR UPDATE OR DELETE` on `screening_results`. It executes the PL/pgSQL function `fn_audit_screening_changes()`, logging the old score, new score, candidate ID, job ID, changing user (`CURRENT_USER`), and timestamp into the append-only `audit_screening_logs` ledger table.

---

### Q9: Why use a Stored Procedure for score recalculation instead of doing it in Python?
> **Answer:** Our stored procedure `sp_batch_recalculate_scores(p_job_id, weights...)` updates hundreds or thousands of candidate scores in-place inside the PostgreSQL database engine. Performing this in Python would require transferring all candidate rows across the network, deserializing them, recalculating, and transmitting update statements back. The stored procedure eliminates network I/O and executes in sub-millisecond time.

---

### Q10: How do you handle database failover and resiliency?
> **Answer:** The SQLAlchemy database engine uses a connection pool with pre-ping (`pool_pre_ping=True`). If the PostgreSQL server is unreachable, the application can either fall back to SQLite for continuous local development, or enforce strict production mode (`REQUIRE_POSTGRES=True`) which raises a fatal error to prevent silent failovers. The `/api/health` endpoint dynamically reports the live engine name, host, and fallback status.

---

### Q11: How do transactions maintain ACID properties in ResumeIQ?
> **Answer:**
> - **Atomicity:** Ensured via `BEGIN`, `COMMIT`, and `ROLLBACK`.
> - **Consistency:** Enforced by 81 database constraints.
> - **Isolation:** Ensured by PostgreSQL's MVCC; critical updates can employ pessimistic row locking with `SELECT ... FOR UPDATE`.
> - **Durability:** Write-Ahead Logging (WAL) ensures committed records persist across system crashes.

---

### Q12: What is Row-Level Security (RLS) and how is it used here?
> **Answer:** RLS restricts which table rows a user or role can read or modify. On the `jobs` table, we configured policies such that all recruiters can read active postings (`p_read_all_jobs`), but only the recruiter who created the posting (`created_by = CURRENT_USER`) is authorized to update or delete it (`p_modify_own_jobs`).

---

### Q13: What does `EXPLAIN (ANALYZE, BUFFERS)` tell you?
> **Answer:** `EXPLAIN` displays the query execution plan generated by the optimizer. `ANALYZE` actually runs the query and outputs real execution times and row counts versus planner estimates. `BUFFERS` reports shared memory buffer hits and reads, distinguishing cached memory access from physical disk I/O.

---

### Q14: How does ResumeIQ handle concurrency and race conditions?
> **Answer:** We demonstrated three levels of concurrency control:
> 1. Multi-Version Concurrency Control (MVCC) prevents readers from blocking writers.
> 2. `SELECT ... FOR UPDATE` acquires row-level locks during active recruiter reviews.
> 3. `SELECT ... FOR UPDATE SKIP LOCKED` allows concurrent background screening workers to pick distinct tasks without deadlock or contention.

---

### Q15: Why is the hybrid ranking score calculated as a formula rather than pure cosine similarity?
> **Answer:** Cosine similarity measures high-level semantic alignment between text embeddings, but cannot strictly enforce categorical prerequisites. The hybrid formula:
> $$\text{Score} = 0.40 \times \text{Semantic} + 0.35 \times \text{Required Skills} + 0.15 \times \text{Preferred Skills} + 0.10 \times \text{Experience}$$
> combines neural NLP semantic matching with deterministic relational constraints.
