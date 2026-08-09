from pathlib import Path
from uuid import uuid4
from backend.app.core.config import get_settings


class TTSService:
    def __init__(self):
        self.settings = get_settings()

    def synthesize(self, text: str) -> str:
        """Create an audio artifact and return its public storage path.

        Phase 1 uses a deterministic placeholder MP3 payload so the API contract,
        storage rules, and downstream media references are production-shaped
        without requiring a vendor key. Swap this method for a provider client.
        """
        filename = f"response_{uuid4().hex}.mp3"
        path = self.settings.audio_dir / filename
        path.write_bytes(b"ID3\x04\x00\x00\x00\x00\x00\x00")
        return f"/storage/audio/{filename}"
