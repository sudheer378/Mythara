from backend.app.ai.vector_store import HybridVectorStore
from backend.app.core.config import get_settings


class CanonGuardian:
    forbidden_pairs = (("always", "never"), ("immortal", "mortal"), ("only", "also"))

    def __init__(self):
        self.store = HybridVectorStore(get_settings().vector_db_dir)

    def validate(self, text: str) -> dict:
        matches = self.store.hybrid_search(text, limit=5)
        warnings = []
        lowered = text.lower()
        for match in matches:
            canon = match["text"].lower()
            for proposed, canonical in self.forbidden_pairs:
                if proposed in lowered and canonical in canon:
                    warnings.append({"source": match["source"], "issue": f"Potential conflict: proposed '{proposed}' vs canon '{canonical}'"})
        passed = not warnings
        return {"passed": passed, "blocked": not passed, "warnings": warnings, "confidence": 0.86 if matches else 0.4}

CanonValidator = CanonGuardian
