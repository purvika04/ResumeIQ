import pytest
from app.services.skill_extractor import skill_extractor

def test_extract_skills_from_text():
    sample_text = (
        "Experienced software developer skilled in Python, React.js, Docker, "
        "and PostgreSQL with 4 years experience building REST APIs."
    )
    skills = skill_extractor.extract_skills(sample_text)
    canonical_names = [s.canonical_name for s in skills]

    assert "Python" in canonical_names
    assert "React" in canonical_names  # Normalized from React.js
    assert "Docker" in canonical_names
    assert "PostgreSQL" in canonical_names
    assert "REST APIs" in canonical_names

def test_skill_boundary_safety():
    # Should NOT match 'go' or 'c' or 'r' inside everyday words
    safe_text = "Good morning! We will go to the park and see the beautiful cloud."
    skills = skill_extractor.extract_skills(safe_text)
    canonical_names = [s.canonical_name for s in skills]

    # Verify no accidental match for Go or C
    assert "Go" not in canonical_names
    assert "C" not in canonical_names

def test_skill_normalization():
    norm_js = skill_extractor.normalize_skill("js")
    assert norm_js is not None
    assert norm_js[0] == "JavaScript"
    assert norm_js[1] == "Programming Languages"

    norm_k8s = skill_extractor.normalize_skill("k8s")
    assert norm_k8s is not None
    assert norm_k8s[0] == "Kubernetes"

    norm_postgres = skill_extractor.normalize_skill("postgres")
    assert norm_postgres is not None
    assert norm_postgres[0] == "PostgreSQL"

def test_skill_evidence_snippet():
    sample_text = "At TechCorp, I developed backend microservices in Python using FastAPI."
    skills = skill_extractor.extract_skills(sample_text)
    fastapi_skill = next((s for s in skills if s.canonical_name == "FastAPI"), None)
    assert fastapi_skill is not None
    assert "FastAPI" in fastapi_skill.evidence_snippet
