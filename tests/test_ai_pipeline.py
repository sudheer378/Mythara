import os
from pathlib import Path

os.environ["MYTHARA_DATABASE_URL"] = "sqlite:///./knowledge/encyclopedia/test.db"

import asyncio
from backend.app.ai.chunking import AdvancedChunker
from backend.app.ai.document import parse_markdown_sections
from backend.app.ai.generator import MytharaAI
from backend.app.core.config import get_settings


def test_markdown_sections_and_recursive_chunks_do_not_write_raw():
    text = "# Fire\n" + ("Fire Mythrals keep ember oaths.\n\n" * 80)
    sections = parse_markdown_sections(text)
    chunks = AdvancedChunker(max_chars=300).chunk_sections("memory.md", sections)
    assert sections[0].title == "Fire"
    assert len(chunks) > 1


def test_create_mythral_writes_to_drafts_not_raw():
    settings = get_settings()
    before = {p: p.stat().st_mtime_ns for p in settings.raw_knowledge_dir.glob("**/*") if p.is_file()}
    path, payload = asyncio.run(MytharaAI().create_mythral_draft("Auralyn", "Fire", "Guardian"))
    after = {p: p.stat().st_mtime_ns for p in settings.raw_knowledge_dir.glob("**/*") if p.is_file()}
    assert before == after
    assert settings.drafts_dir in Path(path).resolve().parents
    assert payload["data"]["name"] == "Auralyn"
