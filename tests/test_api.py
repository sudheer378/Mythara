import os
from pathlib import Path

os.environ["MYTHARA_DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402
from backend.app.core.config import get_settings  # noqa: E402
from backend.app.main import app  # noqa: E402


def test_ask_with_tts_creates_audio_file():
    settings = get_settings()
    raw = settings.raw_knowledge_dir / "test_bible.md"
    raw.write_text("# Mythara Bible\nFire Mythrals respect ember oaths.", encoding="utf-8")
    client = TestClient(app)

    response = client.post("/api/ask", json={"question": "What do Fire Mythrals respect?", "tts": True})

    assert response.status_code == 200
    body = response.json()
    assert "Grounded answer" in body["answer"]
    assert body["audio"].startswith("/storage/audio/")
    assert (settings.repo_root / body["audio"].lstrip("/")).exists()


def test_create_mythral_writes_draft_only_to_drafts():
    client = TestClient(app)

    response = client.post("/api/create/mythral", json={"name": "Auralyn", "type": "Fire", "class": "Guardian"})

    assert response.status_code == 200
    draft_path = Path(response.json()["draft_path"])
    assert "knowledge/drafts" in str(draft_path)
    assert draft_path.exists()
