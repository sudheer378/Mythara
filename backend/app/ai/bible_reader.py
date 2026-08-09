import hashlib
from backend.app.ai.chunking import AdvancedChunker
from backend.app.ai.document import parse_markdown_sections
from backend.app.ai.vector_store import HybridVectorStore
from backend.app.core.config import get_settings


class BibleReader:
    def __init__(self):
        self.settings = get_settings()
        self.vector_store = HybridVectorStore(self.settings.vector_db_dir)
        self.chunker = AdvancedChunker()

    async def ingest(self) -> int:
        documents = []
        for path in sorted(self.settings.raw_knowledge_dir.glob("**/*.md")):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(self.settings.repo_root))
            sections = parse_markdown_sections(text)
            for chunk in self.chunker.chunk_sections(rel, sections):
                chunk["content_hash"] = hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest()
                documents.append(chunk)
        return self.vector_store.upsert_chunks(documents)
