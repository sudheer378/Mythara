from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.db.session import Base, engine
from backend.app.models import entities, mythral  # noqa: F401

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Mythara AI Studio", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
