import pytest
from app.services.scoring_engine import scoring_engine
from app.schemas.screening import ScoringWeights

def test_hybrid_score_calculation():
    job_desc = "Seeking a Full Stack Python Engineer with React and PostgreSQL experience."
    req_skills = ["Python", "React", "PostgreSQL"]
    pref_skills = ["Docker", "AWS"]
    job_min_exp = 3.0

    cand_skills = [
        {"name": "Python", "canonical_name": "Python", "category": "Programming Languages", "evidence_snippet": "Coded in Python."},
        {"name": "React", "canonical_name": "React", "category": "Web Development", "evidence_snippet": "Built React apps."},
        {"name": "PostgreSQL", "canonical_name": "PostgreSQL", "category": "Databases", "evidence_snippet": "Managed PostgreSQL."},
        {"name": "Docker", "canonical_name": "Docker", "category": "Cloud & DevOps", "evidence_snippet": "Dockerized apps."},
    ]

    result = scoring_engine.calculate_score(
        job_description=job_desc,
        job_required_skills=req_skills,
        job_preferred_skills=pref_skills,
        job_min_experience=job_min_exp,
        candidate_resume_text="Senior Python and React full stack developer with PostgreSQL and Docker.",
        candidate_skills=cand_skills,
        candidate_experience_years=4.0,
        candidate_experience_uncertain=False,
    )

    assert 0.0 <= result["overall_score"] <= 100.0
    assert result["required_skill_score"] == 100.0  # 3 of 3 matched
    assert result["preferred_skill_score"] == 50.0   # 1 of 2 matched (Docker, missing AWS)
    assert result["experience_score"] == 100.0       # 4.0 >= 3.0
    assert "Python" in result["matched_required_skills"]
    assert "AWS" in result["missing_preferred_skills"]
    assert result["explanation"] is not None
    assert result["flagged_for_review"] is False

def test_custom_weights_effect():
    job_desc = "Python developer."
    req_skills = ["Python"]
    cand_skills = [{"canonical_name": "Python", "name": "Python"}]

    # Heavy semantic weight
    w_sem = ScoringWeights(weight_semantic=0.8, weight_required_skills=0.1, weight_preferred_skills=0.05, weight_experience=0.05)
    res_sem = scoring_engine.calculate_score(
        job_description=job_desc,
        job_required_skills=req_skills,
        job_preferred_skills=[],
        job_min_experience=1.0,
        candidate_resume_text="Experienced Python coder.",
        candidate_skills=cand_skills,
        candidate_experience_years=2.0,
        custom_weights=w_sem,
    )

    # Heavy skill weight
    w_skill = ScoringWeights(weight_semantic=0.1, weight_required_skills=0.8, weight_preferred_skills=0.05, weight_experience=0.05)
    res_skill = scoring_engine.calculate_score(
        job_description=job_desc,
        job_required_skills=req_skills,
        job_preferred_skills=[],
        job_min_experience=1.0,
        candidate_resume_text="Experienced Python coder.",
        candidate_skills=cand_skills,
        candidate_experience_years=2.0,
        custom_weights=w_skill,
    )

    assert res_sem["overall_score"] > 0
    assert res_skill["overall_score"] > 0
