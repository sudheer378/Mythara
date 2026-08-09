import json
from datetime import datetime, timezone
from pathlib import Path
from backend.app.ai.bible_reader import BibleReader
from backend.app.ai.canon import CanonGuardian
from backend.app.ai.context import ContextBuilder
from backend.app.ai.formatter import format_response
from backend.app.ai.graph_store import GraphStore
from backend.app.ai.llm import LLMEngine
from backend.app.ai.reranker import ReRanker
from backend.app.ai.vector_store import HybridVectorStore
from backend.app.core.cache import cache
from backend.app.core.config import get_settings
from backend.app.utils.security import non_overwriting_path, sanitize_text, safe_slug


class MytharaAI:
    def __init__(self):
        self.settings = get_settings()
        self.store = HybridVectorStore(self.settings.vector_db_dir)
        self.guardian = CanonGuardian()
        self.reranker = ReRanker()
        self.context_builder = ContextBuilder()
        self.llm = LLMEngine()
        self.graph = GraphStore()

    async def ensure_ingested(self) -> int:
        return await BibleReader().ingest()

    async def answer(self, question: str) -> dict:
        question = sanitize_text(question, 4000)
        cache_key = f"ask:{question}"
        cached = await cache.get(cache_key)
        if cached:
            return cached
        await self.ensure_ingested()
        retrieved = self.store.hybrid_search(question, limit=12)
        ranked = self.reranker.rank(question, retrieved, limit=6)
        context = self.context_builder.build(ranked)
        if not ranked:
            answer = "No official Bible material has been indexed yet. Add markdown files to knowledge/raw/ and run ingestion."
        else:
            answer = await self._grounded_answer(question, context["context"])
        canon = self.guardian.validate(answer)
        result = {
            "answer": answer,
            "text": answer,
            "sources": context["sources"],
            "confidence": context["confidence"] if ranked else 0.25,
            "canon_validation": canon,
        }
        await cache.set(cache_key, result, ttl_seconds=300)
        return result

    async def suggest(self, topic: str, focus: str | None = None) -> tuple[Path, dict]:
        topic = sanitize_text(topic, 500)
        answer = await self.answer(f"Canon guidance for improving: {topic}. {focus or ''}")
        content = {
            "topic": topic,
            "focus": focus or "general canon improvement",
            "improvements": [
                "Clarify constraints and consequences already implied by the Bibles.",
                "Strengthen sensory specificity without introducing unapproved canon facts.",
                "Add relationship hooks for encyclopedia and graph consistency.",
            ],
            "grounding": answer["answer"],
            "sources": answer["sources"],
            "confidence": answer["confidence"],
            "canon_validation": answer["canon_validation"],
        }
        path = self._write_json(self.settings.suggestions_dir, f"suggestion_{safe_slug(topic)}", content)
        return path, content

    async def create_mythral_draft(self, name: str, type_: str, mythral_class: str, prompt: str | None = None) -> tuple[Path, dict]:
        await self.ensure_ingested()
        name = sanitize_text(name, 120)
        type_ = sanitize_text(type_, 80)
        mythral_class = sanitize_text(mythral_class, 80)
        brief = sanitize_text(prompt or f"Create a canon-compatible {type_} Mythral.", 4000)
        grounding = await self.answer(f"Canon constraints for a {type_} {mythral_class} Mythral named {name}. {brief}")
        mythral = {
            "entity_type": "mythral",
            "name": name,
            "type": type_,
            "class": mythral_class,
            "description": f"{name} is a {type_} Mythral of the {mythral_class} class, drafted under canon constraints.",
            "abilities": [f"{type_} Attunement", "Bond Resonance", "Lore-Safe Adaptation"],
            "signature_technique": f"{name} Sovereign Technique",
            "passive_ability": "Canonbound Instinct",
            "stats": {"attack": 55, "defense": 50, "speed": 50, "spirit": 60, "bond": 65},
            "weaknesses": ["Unapproved lore drift", "Opposed elemental pressure"],
            "resistances": [type_],
            "habitat": "Pending approved realm assignment",
            "evolution": {"stage": "base", "next": None, "requirements": ["approved bond milestone"]},
            "bond_system": {"affinity": "trust", "growth_trigger": "shared trials", "risk": "bond fracture under contradiction"},
            "lore": f"Drafted from prompt: {brief}",
            "image_path": None,
            "audio_path": None,
            "sources": grounding["sources"],
        }
        canon = self.guardian.validate(json.dumps(mythral))
        if canon["blocked"]:
            mythral["status"] = "blocked_by_canon_guardian"
        response = format_response("mythral_draft", mythral, grounding["confidence"], canon)
        path = self._write_json(self.settings.drafts_dir, f"mythral_{safe_slug(name)}", response)
        self.graph.add_relationships(f"draft:mythral:{name}", [
            {"type": "HAS_ELEMENT", "target": type_},
            {"type": "HAS_CLASS", "target": mythral_class},
            {"type": "HAS_HABITAT", "target": mythral["habitat"]},
        ])
        return path, response

    async def create_entity_draft(self, kind: str, name: str, prompt: str | None = None) -> tuple[Path, dict]:
        grounding = await self.answer(f"Canon constraints for {kind} named {name}. {prompt or ''}")
        entity = {
            "entity_type": kind,
            "name": sanitize_text(name, 120),
            "description": f"Canon-compatible {kind} draft for {name}.",
            "lore": sanitize_text(prompt or "Draft lore pending approval.", 4000),
            "image_path": None,
            "audio_path": None,
            "data": {"sources": grounding["sources"]},
        }
        canon = self.guardian.validate(json.dumps(entity))
        response = format_response(f"{kind}_draft", entity, grounding["confidence"], canon)
        path = self._write_json(self.settings.drafts_dir, f"{kind}_{safe_slug(name)}", response)
        self.graph.add_relationships(f"draft:{kind}:{name}", [{"type": "HAS_STATUS", "target": "draft"}])
        return path, response

    async def _grounded_answer(self, question: str, context: str) -> str:
        result = await self.llm.generate_json(
            "Answer only from supplied Mythara Bible context. If uncertain, say what is missing.",
            f"Question: {question}\n\nContext:\n{context}",
            "grounded_answer",
        )
        return result.get("answer") or f"Based on retrieved official lore, answer this with the following constraints:\n{context[:1800]}"

    def _write_json(self, directory: Path, stem: str, payload: dict) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = non_overwriting_path(directory, f"{stem}_{stamp}", ".json")
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
