from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import get_settings
from backend.app.api.routes import router
from backend.app.db.session import Base, engine
from backend.app.models import entities, mythral  # noqa: F401

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Mythara AI Studio", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
settings = get_settings()
app.mount("/storage", StaticFiles(directory=settings.repo_root / "storage"), name="storage")


@app.get("/health")
def health():
    return {"status": "ok", "system": "Mythara AI Studio"}
