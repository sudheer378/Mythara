import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.agents import AgentOrchestrator
from backend.app.ai.generator import MytharaAI
from backend.app.db.session import get_db
from backend.app.models.schemas import AskRequest, AskResponse, ApproveRequest, ApproveResponse, EntityCreateRequest, MythralCreateRequest, SearchResponse, SuggestRequest, SuggestResponse
from backend.app.services.mythral_service import MythralService
from backend.app.tts.service import TTSService
from backend.app.utils.security import sanitize_text

router = APIRouter(prefix="/api", tags=["studio"])


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    result = await MytharaAI().answer(request.question)
    audio = await TTSService().synthesize(result["answer"]) if request.tts else None
    if request.stream:
        async def events():
            yield json.dumps({"event": "answer", "data": result | {"audio": audio}}) + "\n"
        return StreamingResponse(events(), media_type="application/x-ndjson")
    return AskResponse(text=result["answer"], answer=result["answer"], sources=result["sources"], confidence=result["confidence"], canon_validation=result["canon_validation"], audio=audio)


@router.post("/suggest", response_model=SuggestResponse)
async def suggest(request: SuggestRequest):
    path, content = await MytharaAI().suggest(request.topic, request.focus)
    return SuggestResponse(suggestion_path=str(path), content=json.dumps(content), confidence=content["confidence"], canon_validation=content["canon_validation"])


@router.post("/create/mythral")
async def create_mythral(request: MythralCreateRequest):
    orchestration = await AgentOrchestrator().run({"kind": "mythral", "name": request.name, "type": request.type})
    path, payload = await MytharaAI().create_mythral_draft(request.name, request.type, request.mythral_class, request.prompt)
    payload["orchestration"] = orchestration
    return {"draft_path": str(path), **payload}


@router.post("/create/entity")
async def create_entity(request: EntityCreateRequest):
    path, payload = await MytharaAI().create_entity_draft(request.kind, request.name, request.prompt)
    return {"draft_path": str(path), **payload}


@router.post("/approve", response_model=ApproveResponse)
def approve(request: ApproveRequest, db: Session = Depends(get_db)):
    try:
        path, entity_type, entity_id = MythralService(db).approve_draft(request.draft_path)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=sanitize_text(str(exc), 500)) from exc
    return ApproveResponse(approved_path=str(path), entity_type=entity_type, entity_id=entity_id)


@router.get("/mythral/{mythral_id}")
def get_mythral(mythral_id: int, db: Session = Depends(get_db)):
    mythral = MythralService(db).get(mythral_id)
    if mythral is None:
        raise HTTPException(status_code=404, detail="Mythral not found")
    return mythral


@router.get("/encyclopedia/search", response_model=SearchResponse)
def search_encyclopedia(q: str, db: Session = Depends(get_db)):
    results = MythralService(db).search(sanitize_text(q, 500))
    return SearchResponse(results=results, confidence=0.75 if results else 0.2)
