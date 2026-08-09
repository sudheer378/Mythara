from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str
    tts: bool = False


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    audio: str | None = None


class SuggestRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    focus: str | None = Field(default=None, max_length=1000)


class SuggestResponse(BaseModel):
    suggestion_path: str
    content: str
    confidence: float
    canon_validation: dict


class MythralCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str = Field(min_length=1, max_length=80)
    mythral_class: str = Field(alias="class", min_length=1, max_length=80)
    prompt: str | None = Field(default=None, max_length=4000)
    model_config = ConfigDict(populate_by_name=True)


class EntityCreateRequest(BaseModel):
    kind: Literal["character", "realm", "artifact"]
    name: str
    prompt: str | None = None


class ApproveRequest(BaseModel):
    draft_path: str


class ApproveResponse(BaseModel):
    approved_path: str
    entity_type: str | None = None
    entity_id: int | None = None
    confidence: float = 1.0


class SearchResponse(BaseModel):
    results: list[dict]
    confidence: float
