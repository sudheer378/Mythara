from backend.app.ai.vector_store import JsonVectorStore
from backend.app.core.config import get_settings


class CanonValidator:
    def __init__(self):
        self.store = JsonVectorStore(get_settings().vector_db_dir)

    def validate(self, text: str) -> tuple[bool, list[str]]:
        matches = self.store.search(text, limit=3)
        if not matches:
            return True, ["No Bible chunks indexed yet; validation is advisory."]
        warnings = []
        lowered = text.lower()
        for match in matches:
            if "never" in match["text"].lower() and "always" in lowered:
                warnings.append(f"Potential contradiction with {match['source']}")
        return not warnings, warnings
