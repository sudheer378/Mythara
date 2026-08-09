from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str
    tts: bool = False


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    audio: str | None = None


class SuggestRequest(BaseModel):
    topic: str
    focus: str | None = None


class SuggestResponse(BaseModel):
    suggestion_path: str
    content: str


class MythralCreateRequest(BaseModel):
    name: str
    type: str
    mythral_class: str = Field(alias="class")
    prompt: str | None = None


class ApproveRequest(BaseModel):
    draft_path: str


class ApproveResponse(BaseModel):
    approved_path: str
    mythral_id: int | None = None
