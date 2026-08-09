# Mythara AI Studio

Mythara AI Studio is a personal AI creative operating system for official-lore ingestion, grounded Q&A, canon-safe suggestions, structured draft generation, approval workflow, encyclopedia persistence, vector memory, graph relationships, Redis-backed caching, and voice output.

## Architecture

- `backend/app/api/routes/` FastAPI routes for ask, suggest, create, approve, and encyclopedia search.
- `backend/app/ai/` Bible parsing, recursive chunking, embeddings, hybrid retrieval, reranking, context assembly, LLM integration, canon validation, graph memory, and response formatting.
- `backend/app/agents/` planner, generator, critic, fact checker, reflection, and orchestrator.
- `backend/app/models/` SQLAlchemy models for Mythrals, Characters, Realms, and Artifacts.
- `backend/app/tts/` OpenAI TTS integration with local speech fallback, storing audio in `storage/audio/`.
- `frontend/` minimal studio UI for chat, Mythral creation, approval, encyclopedia search, and audio playback.
- `docker-compose.yml` provisions FastAPI, PostgreSQL, Redis, Qdrant, and Neo4j.

## Run locally

```bash
pip install -e '.[test]'
MYTHARA_DATABASE_URL=sqlite:///./knowledge/encyclopedia/mythara.db uvicorn backend.app.main:app --reload
```

## Run full stack

```bash
docker compose up --build
```

## Rules enforced

- `knowledge/raw/` is read-only application input.
- AI-generated suggestions, drafts, and approvals are written only to the allowed knowledge workflow folders.
- Media bytes are stored in `storage/`; database rows store metadata and file paths only.
- Approved encyclopedia data is persisted to structured DB tables and indexed into vector/graph memory.
