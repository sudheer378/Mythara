import json
from datetime import datetime, timezone
from pathlib import Path
from backend.app.ai.canon import CanonValidator
from backend.app.ai.vector_store import JsonVectorStore
from backend.app.ai.graph_store import JsonGraphStore
from backend.app.core.config import get_settings


class MytharaAI:
    def __init__(self):
        self.settings = get_settings()
        self.store = JsonVectorStore(self.settings.vector_db_dir)
        self.validator = CanonValidator()

    def answer(self, question: str) -> dict:
        chunks = self.store.search(question, limit=4)
        context = "\n\n".join(c["text"] for c in chunks)
        if not chunks:
            answer = "No official Bible material has been indexed yet. Add markdown files to knowledge/raw/ and ingest them."
        else:
            answer = f"Grounded answer based on official lore:\n\n{self._synthesize(question, context)}"
        return {"answer": answer, "sources": sorted({c["source"] for c in chunks})}

    def suggest(self, topic: str, focus: str | None = None) -> tuple[Path, str]:
        result = self.answer(topic)
        content = (
            f"# Suggestion: {topic}\n\n"
            f"Focus: {focus or 'General canon quality'}\n\n"
            "## Improvements\n"
            "- Clarify stakes, limitations, and consequences.\n"
            "- Add sensory detail while preserving established canon.\n"
            "- Ensure named entities match official Bible sources.\n\n"
            f"## Grounding\n{result['answer']}\n"
        )
        path = self._write(self.settings.suggestions_dir, "suggestion", content, "md")
        return path, content

    def create_mythral_draft(self, name: str, type_: str, mythral_class: str, prompt: str | None = None) -> tuple[Path, dict]:
        mythral = {
            "name": name,
            "type": type_,
            "class": mythral_class,
            "description": prompt or f"A {type_} Mythral designed for canon review.",
            "abilities": [f"{type_} attunement", "Bond resonance"],
            "signature_technique": f"{name} Zenith",
            "passive_ability": "Canonbound Instinct",
            "stats": {"attack": 50, "defense": 50, "speed": 50, "spirit": 50},
            "weaknesses": [],
            "resistances": [type_],
            "habitat": "Unassigned",
            "evolution": {"stage": "base", "next": None},
            "bond_system": {"affinity": "trust", "growth_trigger": "shared trials"},
            "lore": "Draft lore pending user approval.",
            "image_path": None,
            "audio_path": None,
        }
        ok, warnings = self.validator.validate(json.dumps(mythral))
        mythral["canon_validation"] = {"passed": ok, "warnings": warnings}
        path = self._write(self.settings.drafts_dir, f"mythral_{name.lower().replace(' ', '_')}", json.dumps(mythral, indent=2), "json")
        JsonGraphStore().add_relationships(f"draft:mythral:{name}", [
            {"type": "HAS_ELEMENT", "target": type_},
            {"type": "HAS_CLASS", "target": mythral_class},
            {"type": "HAS_HABITAT", "target": mythral["habitat"]},
        ])
        return path, mythral

    def _synthesize(self, question: str, context: str) -> str:
        return f"Question: {question}\nRelevant canon excerpts were retrieved and should be used as constraints.\n{context[:1200]}"

    def _write(self, directory: Path, prefix: str, content: str, suffix: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = directory / f"{prefix}_{stamp}.{suffix}"
        path.write_text(content, encoding="utf-8")
        return path
