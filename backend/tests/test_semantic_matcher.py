import pytest
from app.services.semantic_matcher import semantic_matcher

def test_semantic_embedding_generation():
    emb = semantic_matcher.get_embedding("Software Engineer specializing in Python and React.")
    assert emb is not None
    assert emb.shape[0] == 384  # all-MiniLM-L6-v2 dimension

def test_semantic_similarity_range():
    text1 = "Senior Python Developer with FastAPI and Docker experience."
    text2 = "Looking for a Python Backend Engineer who knows FastAPI and Docker."
    text3 = "Pastry chef specializing in artisan French sourdough and croissants."

    high_sim = semantic_matcher.compute_similarity(text1, text2)
    low_sim = semantic_matcher.compute_similarity(text1, text3)

    assert 0.0 <= high_sim <= 100.0
    assert 0.0 <= low_sim <= 100.0
    assert high_sim > low_sim
    assert high_sim >= 65.0
    assert low_sim <= 30.0

def test_embedding_caching():
    text = "Machine Learning Researcher in Natural Language Processing."
    emb1 = semantic_matcher.get_embedding(text)
    emb2 = semantic_matcher.get_embedding(text)
    assert emb1 is emb2 or (emb1 == emb2).all()
