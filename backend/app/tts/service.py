import math
import wave
from uuid import uuid4
from backend.app.core.config import get_settings
from backend.app.utils.security import non_overwriting_path, sanitize_text


class TTSService:
    async def synthesize(self, text: str) -> str:
        settings = get_settings()
        text = sanitize_text(text, 8000)
        if settings.openai_api_key and settings.tts_provider.lower() == "openai":
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                path = non_overwriting_path(settings.audio_dir, f"response_{uuid4().hex}", ".mp3")
                response = await client.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input=text)
                path.write_bytes(response.read())
                return f"/storage/audio/{path.name}"
            except Exception:
                pass
        try:
            import pyttsx3
            path = non_overwriting_path(settings.audio_dir, f"response_{uuid4().hex}", ".wav")
            engine = pyttsx3.init()
            engine.save_to_file(text, str(path))
            engine.runAndWait()
            if path.exists() and path.stat().st_size > 0:
                return f"/storage/audio/{path.name}"
        except Exception:
            pass
        path = non_overwriting_path(settings.audio_dir, f"response_{uuid4().hex}", ".wav")
        self._tone(path, duration_seconds=min(2.5, max(0.5, len(text) / 900)))
        return f"/storage/audio/{path.name}"

    def _tone(self, path, duration_seconds: float) -> None:
        rate = 22050
        amplitude = 12000
        frames = int(rate * duration_seconds)
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(rate)
            for i in range(frames):
                value = int(amplitude * math.sin(2 * math.pi * 440 * i / rate))
                audio.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))
