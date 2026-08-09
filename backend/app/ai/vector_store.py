import json
from pathlib import Path
from backend.app.ai.embeddings import cosine_similarity, embed_text


class HybridVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / "chunks.jsonl"

    def upsert_chunks(self, chunks: list[dict]) -> int:
        existing = {c["id"]: c for c in self._read_all()}
        changed = 0
        for chunk in chunks:
            content_hash = chunk.get("content_hash") or str(hash(chunk["text"]))
            if existing.get(chunk["id"], {}).get("content_hash") == content_hash:
                continue
            chunk["content_hash"] = content_hash
            chunk["embedding"] = embed_text(chunk["text"])
            existing[chunk["id"]] = chunk
            changed += 1
        with self.file.open("w", encoding="utf-8") as fh:
            for chunk in existing.values():
                fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        return changed

    def hybrid_search(self, query: str, limit: int = 8) -> list[dict]:
        query_vector = embed_text(query)
        query_terms = set(query.lower().split())
        scored = []
        for chunk in self._read_all():
            text_terms = set(chunk["text"].lower().split())
            keyword = len(query_terms & text_terms) / max(len(query_terms), 1)
            vector = cosine_similarity(query_vector, chunk["embedding"])
            score = (0.72 * vector) + (0.28 * keyword)
            scored.append((score, chunk))
        return [chunk | {"score": round(score, 4)} for score, chunk in sorted(scored, reverse=True, key=lambda x: x[0])[:limit]]

    search = hybrid_search

    def _read_all(self) -> list[dict]:
        if not self.file.exists():
            return []
        return [json.loads(line) for line in self.file.read_text(encoding="utf-8").splitlines() if line.strip()]
