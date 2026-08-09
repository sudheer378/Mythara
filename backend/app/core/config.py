import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass
class Settings:
    app_name: str = "Mythara AI Studio"
    database_url: str = "postgresql+psycopg://mythara:mythara@postgres:5432/mythara"
    redis_url: str = "redis://redis:6379/0"
    qdrant_url: str = "http://qdrant:6333"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "mythara_password"
    openai_api_key: str | None = None
    tts_provider: str = "local"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    repo_root: Path = Path(__file__).resolve().parents[3]
    raw_knowledge_dir: Path = repo_root / "knowledge" / "raw"
    suggestions_dir: Path = repo_root / "knowledge" / "suggestions"
    drafts_dir: Path = repo_root / "knowledge" / "drafts"
    approved_dir: Path = repo_root / "knowledge" / "approved"
    encyclopedia_dir: Path = repo_root / "knowledge" / "encyclopedia"
    embeddings_dir: Path = repo_root / "knowledge" / "embeddings"
    vector_db_dir: Path = repo_root / "vector_db"
    graph_db_dir: Path = repo_root / "graph_db"
    audio_dir: Path = repo_root / "storage" / "audio"
    image_dir: Path = repo_root / "storage" / "images"
    log_dir: Path = repo_root / "logs"


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(f"MYTHARA_{name}", default)


@lru_cache
def get_settings() -> Settings:
    root = Path(_env("REPO_ROOT", str(Path(__file__).resolve().parents[3]))).resolve()
    settings = Settings(
        app_name=_env("APP_NAME", "Mythara AI Studio") or "Mythara AI Studio",
        database_url=_env("DATABASE_URL", Settings.database_url) or Settings.database_url,
        redis_url=_env("REDIS_URL", Settings.redis_url) or Settings.redis_url,
        qdrant_url=_env("QDRANT_URL", Settings.qdrant_url) or Settings.qdrant_url,
        neo4j_uri=_env("NEO4J_URI", Settings.neo4j_uri) or Settings.neo4j_uri,
        neo4j_user=_env("NEO4J_USER", Settings.neo4j_user) or Settings.neo4j_user,
        neo4j_password=_env("NEO4J_PASSWORD", Settings.neo4j_password) or Settings.neo4j_password,
        openai_api_key=_env("OPENAI_API_KEY"),
        tts_provider=_env("TTS_PROVIDER", "local") or "local",
        embedding_model=_env("EMBEDDING_MODEL", Settings.embedding_model) or Settings.embedding_model,
        reranker_model=_env("RERANKER_MODEL", Settings.reranker_model) or Settings.reranker_model,
        repo_root=root,
    )
    settings.raw_knowledge_dir = root / "knowledge" / "raw"
    settings.suggestions_dir = root / "knowledge" / "suggestions"
    settings.drafts_dir = root / "knowledge" / "drafts"
    settings.approved_dir = root / "knowledge" / "approved"
    settings.encyclopedia_dir = root / "knowledge" / "encyclopedia"
    settings.embeddings_dir = root / "knowledge" / "embeddings"
    settings.vector_db_dir = root / "vector_db"
    settings.graph_db_dir = root / "graph_db"
    settings.audio_dir = root / "storage" / "audio"
    settings.image_dir = root / "storage" / "images"
    settings.log_dir = root / "logs"
    for directory in (
        settings.raw_knowledge_dir, settings.suggestions_dir, settings.drafts_dir,
        settings.approved_dir, settings.encyclopedia_dir, settings.embeddings_dir,
        settings.vector_db_dir, settings.graph_db_dir, settings.audio_dir,
        settings.image_dir, settings.log_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return settings
