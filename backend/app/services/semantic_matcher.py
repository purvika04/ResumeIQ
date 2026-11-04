import os
import hashlib
import logging
from typing import List, Dict, Optional, Union
import numpy as np

# Ensure HuggingFace uses local cache without attempting online network calls
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """Pretrained Sentence-BERT semantic matching engine with LRU caching."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._cache: Dict[str, np.ndarray] = {}
        self._cache_order: List[str] = []
        self._cache_capacity = 2000

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Sentence-BERT model: {self.model_name} on CPU")
            try:
                self._model = SentenceTransformer(self.model_name, device="cpu", local_files_only=True)
            except Exception:
                # Fallback if local_files_only flag causes issues
                self._model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("Sentence-BERT model loaded successfully on CPU.")
        return self._model

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def get_embedding(self, text: str) -> np.ndarray:
        """Returns normalized embedding vector with caching."""
        clean_text = text.strip()
        if not clean_text:
            return np.zeros(384, dtype=np.float32)

        text_hash = self._hash_text(clean_text)
        if text_hash in self._cache:
            # Move to end (most recently used)
            self._cache_order.remove(text_hash)
            self._cache_order.append(text_hash)
            return self._cache[text_hash]

        # Compute embedding using SentenceTransformer
        embedding = self.model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)

        # Cache management
        if len(self._cache) >= self._cache_capacity:
            oldest = self._cache_order.pop(0)
            self._cache.pop(oldest, None)

        self._cache[text_hash] = embedding
        self._cache_order.append(text_hash)
        return embedding

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Computes cosine similarity between two texts normalized to 0.0 - 100.0."""
        if not text1.strip() or not text2.strip():
            return 0.0

        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        # Dot product of normalized vectors equals cosine similarity
        cos_sim = float(np.dot(emb1, emb2))
        
        # Sentence-BERT cosine similarity typically lies between -0.1 and 1.0
        # Calibrate into a clean 0 - 100 score:
        # Clamping negative similarities to 0, and mapping [0, 1] linearly to [0, 100]
        normalized_score = max(0.0, min(100.0, cos_sim * 100.0))
        return round(normalized_score, 2)

    def compute_batch_similarities(self, target_text: str, candidate_texts: List[str]) -> List[float]:
        """Batch computes cosine similarities against a target text."""
        if not candidate_texts:
            return []
        target_emb = self.get_embedding(target_text)
        scores = []
        for c_text in candidate_texts:
            if not c_text.strip():
                scores.append(0.0)
                continue
            c_emb = self.get_embedding(c_text)
            cos_sim = float(np.dot(target_emb, c_emb))
            normalized = max(0.0, min(100.0, cos_sim * 100.0))
            scores.append(round(normalized, 2))
        return scores

# Singleton instance
semantic_matcher = SemanticMatcher()
