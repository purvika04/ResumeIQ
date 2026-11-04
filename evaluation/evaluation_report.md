# ResumeIQ — Evaluation & Performance Report

> [!IMPORTANT]
> Evaluation conducted on the 12-candidate synthetic ground-truth dataset across 3 technical job roles.
> Ranking is performed using the Sentence-BERT (`all-MiniLM-L6-v2`) hybrid scoring engine.

## Overall Information Retrieval (IR) Metrics

| Job Title | Precision@3 | Precision@5 | Recall@5 | MRR | NDCG@5 | Top Candidate | Top Score |
|---|---:|---:|---:|---:|---:|---|---:|
| **Senior Cloud DevOps Engineer** | 0.67 | 0.60 | 1.00 | 1.00 | 0.962 | Marcus Vance | 90.5% |
| **NLP & Machine Learning Engineer** | 1.00 | 0.60 | 1.00 | 1.00 | 1.000 | Dr Elena Rostova | 86.8% |
| **Senior Full Stack Engineer** | 0.67 | 0.60 | 1.00 | 1.00 | 0.947 | Alex Morgan | 85.0% |
| **Mean Average** | **0.78** | **0.60** | **1.00** | **1.00** | **0.970** | — | — |

## Qualitative Breakdown & Analysis

1. **Semantic Separation**: Sentence-BERT cosine embeddings accurately separated cross-domain candidates (e.g. Cybersecurity analyst received <20% similarity on Full Stack & NLP roles).
2. **Strict Skill Constraints**: Candidates missing mandatory skills (e.g. Docker, PostgreSQL) experienced calibrated score penalties, preventing false positive keyword hallucinations.
3. **Experience Thresholding**: Junior profiles were appropriately scored down when minimum experience thresholds were not met, but retained partial credit.

## Real-World Limitations
- Results on synthetic resumes demonstrate algorithmic consistency, but real-world recruitment data contains unconventional formatting, OCR artifacts, and domain nuance requiring human-in-the-loop oversight.
- Candidate screening scores represent job-description alignment and should never replace human interviewing or qualification verification.