import hashlib
import math
from functools import lru_cache
from backend.app.core.config import get_settings

DIMENSIONS = 384


@lru_cache(maxsize=1)
def _sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(get_settings().embedding_model)
    except Exception:
        return None


def embed_text(text: str) -> list[float]:
    model = _sentence_transformer()
    if model is not None:
        return model.encode(text, normalize_embeddings=True).tolist()
    return _deterministic_embedding(text)


def _deterministic_embedding(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "big") % DIMENSIONS
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))
