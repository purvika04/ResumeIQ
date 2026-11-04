import logging
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.screening import ScoringWeights
from app.services.skill_extractor import skill_extractor
from app.services.semantic_matcher import semantic_matcher

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Calculates multi-dimensional compatibility scores and transparent explanations."""

    def __init__(self, default_weights: Optional[ScoringWeights] = None):
        self.default_weights = default_weights or ScoringWeights(
            weight_semantic=0.40,
            weight_required_skills=0.35,
            weight_preferred_skills=0.15,
            weight_experience=0.10,
        )

    def calculate_score(
        self,
        job_description: str,
        job_required_skills: List[str],
        job_preferred_skills: List[str],
        job_min_experience: float,
        candidate_resume_text: str,
        candidate_skills: List[Dict[str, Any]],  # List of skill items with name, canonical_name, evidence_snippet
        candidate_experience_years: float,
        candidate_experience_uncertain: bool = False,
        custom_weights: Optional[ScoringWeights] = None,
    ) -> Dict[str, Any]:
        """Calculates final hybrid score and evidence breakdown."""
        weights = custom_weights or self.default_weights

        # 1. Semantic Similarity Score (0 - 100)
        semantic_score = semantic_matcher.compute_similarity(job_description, candidate_resume_text)

        # 2. Skill Normalization and Matching
        candidate_canonical_skills = {
            s.get("canonical_name", s.get("name", "")).strip().lower(): s
            for s in candidate_skills
        }

        # Match Required Skills
        matched_required: List[str] = []
        missing_required: List[str] = []
        evidence_snippets: Dict[str, str] = {}

        for req_skill in job_required_skills:
            normalized = skill_extractor.normalize_skill(req_skill)
            canonical_name = normalized[0] if normalized else req_skill.strip()
            key = canonical_name.lower()

            if key in candidate_canonical_skills:
                matched_required.append(canonical_name)
                # Store snippet if available
                snippet = candidate_canonical_skills[key].get("evidence_snippet")
                if snippet:
                    evidence_snippets[canonical_name] = snippet
            else:
                missing_required.append(canonical_name)

        if job_required_skills:
            required_skill_score = (len(matched_required) / len(job_required_skills)) * 100.0
        else:
            required_skill_score = 100.0

        # Match Preferred Skills
        matched_preferred: List[str] = []
        missing_preferred: List[str] = []

        for pref_skill in job_preferred_skills:
            normalized = skill_extractor.normalize_skill(pref_skill)
            canonical_name = normalized[0] if normalized else pref_skill.strip()
            key = canonical_name.lower()

            if key in candidate_canonical_skills:
                matched_preferred.append(canonical_name)
                snippet = candidate_canonical_skills[key].get("evidence_snippet")
                if snippet and canonical_name not in evidence_snippets:
                    evidence_snippets[canonical_name] = snippet
            else:
                missing_preferred.append(canonical_name)

        if job_preferred_skills:
            preferred_skill_score = (len(matched_preferred) / len(job_preferred_skills)) * 100.0
        else:
            preferred_skill_score = 100.0

        # 3. Experience Score (0 - 100)
        if job_min_experience <= 0:
            experience_score = 100.0
        else:
            if candidate_experience_years >= job_min_experience:
                experience_score = 100.0
            else:
                experience_score = max(0.0, (candidate_experience_years / job_min_experience) * 100.0)

        # 4. Final Hybrid Weighted Score
        final_score = (
            weights.weight_semantic * semantic_score
            + weights.weight_required_skills * required_skill_score
            + weights.weight_preferred_skills * preferred_skill_score
            + weights.weight_experience * experience_score
        )
        final_score = round(max(0.0, min(100.0, final_score)), 2)

        # Review Flags
        flagged_for_review = False
        flag_reasons = []

        if candidate_experience_uncertain:
            flagged_for_review = True
            flag_reasons.append("Experience timeline could not be fully parsed with certainty; manual review advised.")

        if len(missing_required) > 0 and len(matched_required) == 0:
            flagged_for_review = True
            flag_reasons.append("Zero required core skills detected in resume.")

        if semantic_score < 30.0 and final_score > 60.0:
            flagged_for_review = True
            flag_reasons.append("Discrepancy detected: high keyword coverage but low semantic context similarity.")

        # 5. Transparent Human-Readable Explanation
        explanation_parts = []
        explanation_parts.append(
            f"Overall compatibility of {final_score:.1f}% based on semantic alignment ({semantic_score:.1f}%), "
            f"required skills coverage ({required_skill_score:.1f}%), preferred skills ({preferred_skill_score:.1f}%), "
            f"and experience suitability ({experience_score:.1f}%)."
        )

        if matched_required:
            explanation_parts.append(f"Demonstrated core skills: {', '.join(matched_required[:5])}.")
        if missing_required:
            explanation_parts.append(f"Skill gaps identified: {', '.join(missing_required[:5])}.")
        if matched_preferred:
            explanation_parts.append(f"Bonus qualifications: {', '.join(matched_preferred[:4])}.")

        if job_min_experience > 0:
            exp_status = "meets" if candidate_experience_years >= job_min_experience else "below"
            explanation_parts.append(
                f"Candidate has {candidate_experience_years:.1f} estimated years vs {job_min_experience:.1f} required ({exp_status} target)."
            )

        explanation = " ".join(explanation_parts)

        return {
            "overall_score": final_score,
            "semantic_score": round(semantic_score, 2),
            "required_skill_score": round(required_skill_score, 2),
            "preferred_skill_score": round(preferred_skill_score, 2),
            "experience_score": round(experience_score, 2),
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "evidence_snippets": evidence_snippets,
            "explanation": explanation,
            "flagged_for_review": flagged_for_review,
            "flag_reason": "; ".join(flag_reasons) if flag_reasons else None,
            "weights_used": weights.model_dump(),
        }

# Singleton instance
scoring_engine = ScoringEngine()
