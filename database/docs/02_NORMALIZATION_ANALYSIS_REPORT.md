# ResumeIQ: Relational Normalization Analysis Report (1NF through BCNF)

This report documents the relational normalization progression of ResumeIQ from First Normal Form (1NF) through Boyce-Codd Normal Form (BCNF), with mathematical functional dependency (FD) proofs.

---

## 1. Normalization Journey Overview

| Normal Form | Condition Required | ResumeIQ Implementation Status | Architectural Mechanism |
|---|---|---|---|
| **1NF** (First Normal Form) | All attribute values are atomic; no repeating groups. | **SATISFIED** | Decomposed candidate educations, experiences, and skills out of JSON arrays into separate relational child tables. |
| **2NF** (Second Normal Form) | In 1NF + No partial functional dependencies on any candidate key. | **SATISFIED** | In composite tables (`candidate_skills`, `job_skills`, `screening_results`, `applications`), all non-key attributes depend on the full composite key. |
| **3NF** (Third Normal Form) | In 2NF + No transitive functional dependencies ($X \to Y$ and $Y \to Z$). | **SATISFIED** | Skill taxonomies separated into `skills` table; recruiters separated from `jobs`; candidate details separated from `applications`. |
| **BCNF** (Boyce-Codd Normal Form) | For every non-trivial FD $X \to Y$, $X$ must be a superkey. | **SATISFIED** across core relational structures. | All functional dependencies originate from candidate keys (`id`, `email`, or composite unique keys). |

---

## 2. Mathematical Functional Dependency (FD) Analysis

### Candidate Table:
- **Primary Key:** `{id}`
- **Candidate Keys:** `{id}`, `{email}`
- **Functional Dependencies:**
  $$\{id\} \to \{\text{name}, \text{email}, \text{phone}, \text{current\_role}, \text{total\_experience\_years}, \text{location}, \text{resume\_doc\_id}\}$$
  $$\{\text{email}\} \to \{id, \text{name}, \dots\}$$
- **Verification:** Both left-hand sides are superkeys. No partial or transitive dependencies exist $\implies$ **BCNF satisfied**.

### Decomposition of Candidate Educations (1NF Enhancement):
- **Problem in unnormalized design:** Storing `[{"degree": "BS", "inst": "MIT"}, {"degree": "MS", "inst": "Stanford"}]` as an array violates 1NF atomicity.
- **Normalized Relation:** `candidate_educations(id, candidate_id, degree, institution, field_of_study, graduation_year, gpa)`
- **FDs:**
  $$\{id\} \to \{\text{candidate\_id}, \text{degree}, \text{institution}, \text{field\_of\_study}, \text{graduation\_year}, \text{gpa}\}$$
  $$\text{candidate\_id} \to \text{educations is } 1:N \text{ (non-functional)}$$
- **Conclusion:** 1NF violation eradicated. Each degree is an atomic tuple.

### Decomposition of Candidate Experiences (1NF Enhancement):
- **Normalized Relation:** `candidate_experiences(id, candidate_id, title, company, location, start_date, end_date, is_current, description)`
- **Conclusion:** Repeating career histories are strictly first-class relational entities with atomic temporal boundaries.

### Composite Linkage Tables (2NF & 3NF):
- **Table:** `candidate_skills(id, candidate_id, skill_id, skill_name, category, proficiency, years_experience)`
  - Composite key constraint: `UNIQUE(candidate_id, skill_name)`
  - Attribute `proficiency` depends strictly on the pair $(\text{candidate\_id}, \text{skill\_name})$. A candidate cannot have a generic proficiency in isolation without the candidate identity.
  - Foreign key `skill_id \to skills(id)` ensures canonical skill categories are governed centrally without transitive anomalies.

- **Table:** `screening_results(id, job_id, candidate_id, overall_score, semantic_score, required_skill_score, preferred_skill_score, experience_score, explanation, flagged_for_review)`
  - Composite key constraint: `UNIQUE(job_id, candidate_id)`
  - All score dimensions represent the mathematical compatibility of *one candidate* evaluated against *one specific job posting*.
  - No score can exist if either `job_id` or `candidate_id` is omitted.
  - Left-hand determinant $\{job\_id, candidate\_id\}$ is a valid candidate key $\implies$ **2NF & 3NF satisfied**.

---

## 3. Deliberate Hybrid Design Decisions (Denormalization vs 3NF)

In modern AI-assisted DBMS architectures, full 3NF normalization is balanced against real-time API latency requirements:

1. **Document Store JSON Sidecars (`matched_skills_json`, `evidence_snippets_json` in `screening_results`):**
   - The relational columns (`overall_score`, `semantic_score`, `flagged_for_review`) are fully indexed and structured for query filters and sorting.
   - The detailed Sentence-BERT textual quote snippets and explanations are stored as JSON text payloads to eliminate high-latency recursive table joins when rendering candidate scorecards.
2. **`total_experience_years` in `candidates`:**
   - Pre-computed and cached during initial resume parsing.
   - Supported by PL/pgSQL function `fn_calculate_candidate_experience_tenure(id)` which computes tenure dynamically from `candidate_experiences` whenever re-audit is demanded.
