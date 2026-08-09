from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.ai.bible_reader import BibleReader
from backend.app.ai.generator import MytharaAI
from backend.app.db.session import get_db
from backend.app.models.schemas import AskRequest, AskResponse, ApproveRequest, ApproveResponse, MythralCreateRequest, SuggestRequest, SuggestResponse
from backend.app.services.mythral_service import MythralService
from backend.app.tts.service import TTSService

router = APIRouter(prefix="/api")


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    BibleReader().ingest()
    result = MytharaAI().answer(request.question)
    audio = TTSService().synthesize(result["answer"]) if request.tts else None
    return AskResponse(answer=result["answer"], sources=result["sources"], audio=audio)


@router.post("/suggest", response_model=SuggestResponse)
def suggest(request: SuggestRequest):
    BibleReader().ingest()
    path, content = MytharaAI().suggest(request.topic, request.focus)
    return SuggestResponse(suggestion_path=str(path), content=content)


@router.post("/create/mythral")
def create_mythral(request: MythralCreateRequest):
    BibleReader().ingest()
    path, mythral = MytharaAI().create_mythral_draft(request.name, request.type, request.mythral_class, request.prompt)
    return {"draft_path": str(path), "mythral": mythral}


@router.post("/approve", response_model=ApproveResponse)
def approve(request: ApproveRequest, db: Session = Depends(get_db)):
    try:
        path, mythral = MythralService(db).approve_draft(request.draft_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApproveResponse(approved_path=str(path), mythral_id=mythral.id if mythral else None)


@router.get("/mythral/{mythral_id}")
def get_mythral(mythral_id: int, db: Session = Depends(get_db)):
    mythral = MythralService(db).get(mythral_id)
    if mythral is None:
        raise HTTPException(status_code=404, detail="Mythral not found")
    return mythral
