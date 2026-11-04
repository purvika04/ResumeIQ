# ResumeIQ — AI-Powered Resume Screening & Candidate Ranking System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)
[![Sentence--Transformers](https://img.shields.io/badge/S--BERT-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**ResumeIQ** is an enterprise-grade recruitment intelligence platform that analyzes candidate resumes using Natural Language Processing (NLP), extracts structured competencies, computes multidimensional semantic compatibility using **Sentence-BERT (`all-MiniLM-L6-v2`)**, identifies critical skill gaps, and ranks candidates with transparent, explainable evidence.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph UI["Recruiter Web Dashboard (React + Vite + Tailwind)"]
        O[Overview Dashboard]
        U[Multi-Resume Upload]
        J[Job Descriptions Manager]
        R[Candidate Rankings & Weights]
        D[Candidate Detail & Evidence Profile]
        A[Analytics & Competency Metrics]
    end

    subgraph API["FastAPI REST Backend (Port 8000)"]
        EP["API Endpoints (/api/*)"]
        RP["Resume Parser (PyMuPDF + docx)"]
        SE["Skill Extractor & Normalizer (spaCy / Regex)"]
        SM["Semantic Matcher (Sentence-BERT CPU Singleton)"]
        SC["Scoring Engine (Hybrid Formula)"]
        RE["Ranking Engine & XAI Generator"]
    end

    subgraph DataStore["Dual-Mode Database Layer"]
        subgraph Relational["Relational Storage (Supabase / SQLite)"]
            PG[(Supabase PostgreSQL / SQLite)]
            T1[Recruiters, Candidates, Jobs]
            T2[CandidateSkills, JobSkills]
            T3[ScreeningResults, Interviews]
        end
        subgraph Document["Document Storage (MongoDB / JSON)"]
            MG[(MongoDB / Local JSON Store)]
            D1[resumes_raw]
            D2[resumes_parsed]
            D3[nlp_logs]
        end
    end

    U -->|PDF / DOCX Upload| EP
    EP --> RP --> SE
    SE --> SM --> SC --> RE
    RE --> PG & MG
    PG & MG --> EP --> UI
```

---

## 2. Core Modules & Methodology

### Module 1: Resume Upload and Ingestion
- Supports batch uploads of **PDF**, **DOCX**, and **TXT** resumes.
- Automated sanitization, Unicode normalization, and header/footer cleanup.
- Boundary-safe contact extraction (Email, Phone, LinkedIn, GitHub) via validated regex expressions.
- Educational credential recognition (Degrees, Institutions, Graduation Years).
- Chronological work history segmentation and duration estimation.
- Gracefully handles malformed documents and flags uncertain extractions.

### Module 2: NLP Skill Extraction & Taxonomy
- Configurable taxonomy spanning **7+ engineering categories**:
  - Programming Languages (Python, Java, Go, TypeScript, C++, etc.)
  - Web Development (FastAPI, React, Django, Node.js, Next.js, etc.)
  - Databases (PostgreSQL, MongoDB, Redis, SQLite, etc.)
  - Cloud & DevOps (AWS, Docker, Kubernetes, Terraform, CI/CD, etc.)
  - AI / ML & Data Science (PyTorch, Transformers, spaCy, Pandas, etc.)
  - Software Engineering Tools (Microservices, Agile, Unit Testing, etc.)
  - Cybersecurity (OWASP, Penetration Testing, IAM, Cryptography, etc.)
- Canonical normalization and alias detection (e.g. `JS` → `JavaScript`, `K8s` → `Kubernetes`, `React.js` → `React`).
- Boundary-safe matching (`\b`) preventing substrings inside unrelated English vocabulary.
- Contextual quote extraction: captures the exact sentence where a skill was used as verifiable evidence.

### Module 3 & 4: Semantic Matching & Hybrid Ranking
- **Pretrained Sentence-BERT**: `sentence-transformers/all-MiniLM-L6-v2` loaded once on CPU with an LRU embedding cache.
- Cosine similarity between resume embeddings and job descriptions calibrated to a 0–100 scale.
- **Hybrid Scoring Formula**:
  $$\text{Final Score} = w_1 \cdot \text{Semantic} + w_2 \cdot \text{ReqSkills} + w_3 \cdot \text{PrefSkills} + w_4 \cdot \text{Experience}$$
  *(Default weights: 40% Semantic, 35% Required Skills, 15% Preferred Skills, 10% Experience)*.
- Recruiter-controlled weight sliders directly in the UI.

### Module 5: Explainable AI (XAI)
- Transparent score breakdown radar chart.
- Clear separation of verified matches and missing skill gaps.
- Exact verifiable resume excerpt quotations for every matched skill.
- Automated anomaly detection flagging candidates with high keyword overlap but low semantic context similarity.
- **Ethical Safeguard**: Demographic characteristics are excluded from evaluation. The platform serves as recruiter decision-support, not an autonomous hiring authority.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2, Python-Multipart |
| **AI / ML** | Sentence-Transformers (`all-MiniLM-L6-v2`), PyTorch (CPU-optimized), spaCy, Scikit-Learn, NumPy, Pandas |
| **Resume Processing** | PyMuPDF (`fitz`), `python-docx`, Regular Expressions |
| **Relational Database** | Supabase (PostgreSQL) with seamless local SQLite fallback |
| **Document Store** | MongoDB Atlas with seamless local atomic JSON fallback |
| **Testing** | Pytest, FastAPI TestClient, Automated IR Evaluation (NDCG, MRR, P@K) |

---

## 4. Setup and Installation

### Prerequisites
- Python 3.11
- Node.js (v18+) & npm

### Clone and Environment Setup
```bash
cd resumeiq

# 1. Setup Backend Virtual Environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup Frontend Dependencies
cd ../frontend
npm install
```

---

## 5. Configuration & Database Modes

ResumeIQ supports **Zero-Configuration Local Development** by default, and seamlessly connects to **Supabase** and **MongoDB** when credentials are provided in `.env`.

### Local Development (Default Out-of-the-Box)
No external database setup required. ResumeIQ uses:
- Relational: `sqlite:///backend/data/resumeiq.db`
- Document: `backend/data/document_store/` (atomic JSON store)

### Production Mode (Supabase PostgreSQL + MongoDB)
Create `backend/.env` (or copy from `backend/.env.example`):
```env
# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

# MongoDB Atlas
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=resumeiq_db
```
SQL migration file is available at:
`database/migrations/001_initial_schema.sql`

---

## 6. Running the Application

### Start Backend API Server
```bash
cd resumeiq/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

### Start Frontend Development Server
In a separate terminal:
```bash
cd resumeiq/frontend
npm run dev
```
- Frontend Dashboard: `http://localhost:5173`

---

## 7. Automated Testing & Evaluation

### Run Pytest Test Suite
```bash
cd resumeiq/backend
source venv/bin/activate
pytest tests/ -v
```
**Test Coverage Includes:**
- Text extraction (PDF, DOCX, TXT)
- Boundary-safe skill extraction
- Alias normalization
- Sentence-BERT embedding generation and caching
- Hybrid scoring engine calculations
- Candidate ranking ordering
- REST API CRUD and file upload endpoints

### Run Information Retrieval (IR) Evaluation
```bash
cd resumeiq
backend/venv/bin/python evaluation/evaluate_ranking.py
```

### Evaluation Results (12 Synthetic Candidates across 3 Technical Roles)

| Job Role | Precision@3 | Precision@5 | Recall@5 | MRR | NDCG@5 | Top Candidate | Match Score |
|---|---:|---:|---:|---:|---:|---|---:|
| **Senior Cloud DevOps Engineer** | 0.67 | 0.60 | 1.00 | 1.00 | **0.962** | Marcus Vance | 90.5% |
| **NLP & Machine Learning Engineer** | 1.00 | 0.60 | 1.00 | 1.00 | **1.000** | Dr. Elena Rostova | 86.8% |
| **Senior Full Stack Engineer** | 0.67 | 0.60 | 1.00 | 1.00 | **0.947** | Alex Morgan | 85.0% |
| **Aggregate Mean** | **0.78** | **0.60** | **1.00** | **1.00** | **0.970** | — | — |

Detailed evaluation report generated at: [`evaluation/evaluation_report.md`](evaluation/evaluation_report.md).

---

## 8. Responsible AI & Limitations

1. **Human Oversight**: ResumeIQ is designed as recruiter decision support. Algorithmic scores must not serve as autonomous hiring determinations.
2. **Format Sensitivity**: While PyMuPDF and python-docx handle standard resume layouts, creative graphic resumes (multi-column tables, scanned images without OCR) may experience reduced extraction accuracy.
3. **Synthetic vs. Real-World Data**: Benchmarks are performed against synthetic ground truth. In production environments, regional jargon and diverse resume templates require periodic taxonomy maintenance.
