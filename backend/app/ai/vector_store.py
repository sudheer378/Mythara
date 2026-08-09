import json
from pathlib import Path
from backend.app.ai.embeddings import cosine_similarity, embed_text


class JsonVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / "chunks.jsonl"

    def upsert_chunks(self, chunks: list[dict]) -> int:
        existing = {c["id"]: c for c in self._read_all()}
        for chunk in chunks:
            chunk["embedding"] = embed_text(chunk["text"])
            existing[chunk["id"]] = chunk
        with self.file.open("w", encoding="utf-8") as fh:
            for chunk in existing.values():
                fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        return len(chunks)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        query_vector = embed_text(query)
        scored = []
        for chunk in self._read_all():
            scored.append((cosine_similarity(query_vector, chunk["embedding"]), chunk))
        return [chunk | {"score": score} for score, chunk in sorted(scored, reverse=True, key=lambda x: x[0])[:limit]]

    def _read_all(self) -> list[dict]:
        if not self.file.exists():
            return []
        return [json.loads(line) for line in self.file.read_text(encoding="utf-8").splitlines() if line.strip()]
