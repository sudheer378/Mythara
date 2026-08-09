from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mythara AI Studio"
    database_url: str = "sqlite:///./knowledge/encyclopedia/mythara.db"
    repo_root: Path = Path(__file__).resolve().parents[3]
    raw_knowledge_dir: Path = repo_root / "knowledge" / "raw"
    suggestions_dir: Path = repo_root / "knowledge" / "suggestions"
    drafts_dir: Path = repo_root / "knowledge" / "drafts"
    approved_dir: Path = repo_root / "knowledge" / "approved"
    vector_db_dir: Path = repo_root / "vector_db"
    graph_db_dir: Path = repo_root / "graph_db"
    audio_dir: Path = repo_root / "storage" / "audio"
    model_config = SettingsConfigDict(env_prefix="MYTHARA_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for directory in (
        settings.raw_knowledge_dir,
        settings.suggestions_dir,
        settings.drafts_dir,
        settings.approved_dir,
        settings.vector_db_dir,
        settings.graph_db_dir,
        settings.audio_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return settings
