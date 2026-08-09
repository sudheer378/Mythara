import json
from pathlib import Path
from shutil import copyfile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from backend.app.ai.embeddings import embed_text
from backend.app.ai.graph_store import GraphStore
from backend.app.ai.vector_store import HybridVectorStore
from backend.app.core.config import get_settings
from backend.app.models.entities import Artifact, Character, Realm
from backend.app.models.mythral import Mythral
from backend.app.utils.security import ensure_child_path, non_overwriting_path


class MythralService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.vector_store = HybridVectorStore(self.settings.vector_db_dir)
        self.graph = GraphStore()

    def get(self, mythral_id: int) -> Mythral | None:
        return self.db.get(Mythral, mythral_id)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        like = f"%{query}%"
        rows = self.db.execute(select(Mythral).where(or_(Mythral.name.ilike(like), Mythral.description.ilike(like))).limit(limit)).scalars().all()
        db_results = [{"entity_type": "mythral", "id": r.id, "name": r.name, "description": r.description} for r in rows]
        vector_results = self.vector_store.hybrid_search(query, limit=limit)
        return db_results + [{"entity_type": "lore_chunk", **r} for r in vector_results]

    def approve_draft(self, draft_path: str) -> tuple[Path, str | None, int | None]:
        requested = Path(draft_path)
        raw = requested if requested.is_absolute() else self.settings.repo_root / draft_path.lstrip("/")
        source = ensure_child_path(self.settings.drafts_dir, raw)
        data = json.loads(source.read_text(encoding="utf-8"))
        payload = data.get("data", data)
        if data.get("canon_validation", {}).get("blocked"):
            raise ValueError("Canon Guardian blocked this draft; resolve contradictions before approval")
        target = non_overwriting_path(self.settings.approved_dir, source.stem, source.suffix)
        copyfile(source, target)
        entity_type = payload.get("entity_type")
        entity_id = None
        if entity_type == "mythral":
            entity = Mythral(
                name=payload["name"], type=payload["type"], mythral_class=payload["class"],
                description=payload.get("description", ""), abilities=payload.get("abilities", []),
                signature_technique=payload.get("signature_technique", ""), passive_ability=payload.get("passive_ability", ""),
                stats=payload.get("stats", {}), weaknesses=payload.get("weaknesses", []), resistances=payload.get("resistances", []),
                habitat=payload.get("habitat", ""), evolution=payload.get("evolution", {}), bond_system=payload.get("bond_system", {}),
                lore=payload.get("lore", ""), image_path=payload.get("image_path"), audio_path=payload.get("audio_path"),
            )
            self.db.add(entity); self.db.commit(); self.db.refresh(entity)
            entity_id = entity.id
        elif entity_type in {"character", "realm", "artifact"}:
            model = {"character": Character, "realm": Realm, "artifact": Artifact}[entity_type]
            entity = model(name=payload["name"], description=payload.get("description", ""), lore=payload.get("lore", ""), audio_path=payload.get("audio_path"), data=payload.get("data", {}))
            self.db.add(entity); self.db.commit(); self.db.refresh(entity)
            entity_id = entity.id
        if entity_type and entity_id:
            text = json.dumps(payload, ensure_ascii=False)
            self.vector_store.upsert_chunks([{"id": f"approved:{entity_type}:{entity_id}", "source": str(target.relative_to(self.settings.repo_root)), "section": entity_type, "text": text, "embedding": embed_text(text)}])
            self.graph.add_relationships(f"approved:{entity_type}:{entity_id}", [{"type": "APPROVED_AS", "target": entity_type}])
        return target, entity_type, entity_id
