from pathlib import Path
from backend.app.core.config import get_settings
from backend.app.ai.vector_store import JsonVectorStore


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


class BibleReader:
    def __init__(self):
        self.settings = get_settings()
        self.vector_store = JsonVectorStore(self.settings.vector_db_dir)

    def ingest(self) -> int:
        documents = []
        for path in sorted(self.settings.raw_knowledge_dir.glob("**/*.md")):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(self.settings.repo_root))
            for index, chunk in enumerate(chunk_text(text)):
                documents.append({"id": f"{rel}:{index}", "source": rel, "text": chunk})
        return self.vector_store.upsert_chunks(documents)
