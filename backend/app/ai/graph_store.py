import json
from pathlib import Path
from backend.app.core.config import get_settings


class GraphStore:
    def __init__(self, path: Path | None = None):
        self.path = path or get_settings().graph_db_dir
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / "relationships.json"
        self._driver = None
        try:
            from neo4j import GraphDatabase
            s = get_settings()
            self._driver = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))
        except Exception:
            self._driver = None

    def add_relationships(self, entity_id: str, relationships: list[dict]) -> None:
        if self._driver:
            with self._driver.session() as session:
                for rel in relationships:
                    session.run(
                        "MERGE (a:Entity {id:$entity_id}) MERGE (b:Entity {id:$target}) MERGE (a)-[:RELATED {type:$type}]->(b)",
                        entity_id=entity_id, target=rel["target"], type=rel["type"],
                    )
        graph = self._load()
        graph[entity_id] = relationships
        self.file.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    def _load(self) -> dict:
        if not self.file.exists():
            return {}
        return json.loads(self.file.read_text(encoding="utf-8"))

JsonGraphStore = GraphStore
