import json
from pathlib import Path
from shutil import copyfile
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.models.mythral import Mythral


class MythralService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get(self, mythral_id: int) -> Mythral | None:
        return self.db.get(Mythral, mythral_id)

    def approve_draft(self, draft_path: str) -> tuple[Path, Mythral | None]:
        source = (self.settings.repo_root / draft_path.lstrip("/")).resolve()
        if self.settings.raw_knowledge_dir in source.parents:
            raise ValueError("knowledge/raw is read-only and cannot be approved from directly")
        if self.settings.drafts_dir not in source.parents:
            raise ValueError("Only files from knowledge/drafts can be approved")
        data = json.loads(source.read_text(encoding="utf-8")) if source.suffix == ".json" else None
        target = self.settings.approved_dir / source.name
        copyfile(source, target)
        mythral = None
        if data and {"name", "type", "class"}.issubset(data):
            mythral = Mythral(
                name=data["name"], type=data["type"], mythral_class=data["class"],
                description=data.get("description", ""), abilities=data.get("abilities", []),
                signature_technique=data.get("signature_technique", ""), passive_ability=data.get("passive_ability", ""),
                stats=data.get("stats", {}), weaknesses=data.get("weaknesses", []), resistances=data.get("resistances", []),
                habitat=data.get("habitat", ""), evolution=data.get("evolution", {}), bond_system=data.get("bond_system", {}),
                lore=data.get("lore", ""), image_path=data.get("image_path"), audio_path=data.get("audio_path"),
            )
            self.db.add(mythral)
            self.db.commit()
            self.db.refresh(mythral)
        return target, mythral
