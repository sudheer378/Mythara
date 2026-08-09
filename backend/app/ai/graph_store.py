import json
from pathlib import Path
from backend.app.core.config import get_settings


class JsonGraphStore:
    def __init__(self, path: Path | None = None):
        self.path = path or get_settings().graph_db_dir
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / "relationships.json"

    def add_relationships(self, entity_id: str, relationships: list[dict]) -> None:
        graph = self._load()
        graph[entity_id] = relationships
        self.file.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    def _load(self) -> dict:
        if not self.file.exists():
            return {}
        return json.loads(self.file.read_text(encoding="utf-8"))
