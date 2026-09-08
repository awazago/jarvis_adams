from typing import Literal, Optional
from pydantic import BaseModel

Area = Literal["metas", "trabalho", "projetos", "financas", "aprendizado", "saude", "relacoes", "meta"]


class NoteBase(BaseModel):
    area: Area
    title: str
    body: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    area: Optional[Area] = None
    title: Optional[str] = None
    body: Optional[str] = None


class NoteOut(NoteBase):
    id: str

    class Config:
        from_attributes = True


class RelationOut(BaseModel):
    id: str
    note_a: str
    note_b: str

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    saved_note: Optional[NoteOut] = None
