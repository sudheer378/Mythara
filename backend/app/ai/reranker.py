from functools import lru_cache
from backend.app.core.config import get_settings


@lru_cache(maxsize=1)
def _cross_encoder():
    try:
        from sentence_transformers import CrossEncoder
        return CrossEncoder(get_settings().reranker_model)
    except Exception:
        return None


class ReRanker:
    def rank(self, query: str, chunks: list[dict], limit: int = 5) -> list[dict]:
        model = _cross_encoder()
        if model and chunks:
            scores = model.predict([(query, chunk["text"]) for chunk in chunks])
            ranked = sorted(zip(scores, chunks), reverse=True, key=lambda item: float(item[0]))
            return [chunk | {"rerank_score": round(float(score), 4)} for score, chunk in ranked[:limit]]
        return sorted(chunks, reverse=True, key=lambda chunk: chunk.get("score", 0))[:limit]
