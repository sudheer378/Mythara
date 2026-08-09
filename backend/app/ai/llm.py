import json
from backend.app.core.config import get_settings


class LLMEngine:
    async def generate_json(self, system: str, user: str, schema_name: str) -> dict:
        settings = get_settings()
        if settings.openai_api_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                response = await client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    response_format={"type": "json_object"},
                )
                return json.loads(response.choices[0].message.content or "{}")
            except Exception:
                pass
        return {"schema": schema_name, "content": user[:2400], "confidence": 0.62}
