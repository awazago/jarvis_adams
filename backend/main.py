import re
import httpx
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db, Base
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, CORS_ORIGINS

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAVE_REGEX = re.compile(r"\[\[SAVE:([a-z_]+)\|([^|]+)\|([\s\S]+?)\]\]")


# ---------- NOTES ----------
@app.get("/notes", response_model=list[schemas.NoteOut])
def get_notes(db: Session = Depends(get_db)):
    return crud.list_notes(db)


@app.post("/notes", response_model=schemas.NoteOut)
def post_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, note.area, note.title, note.body)


@app.put("/notes/{note_id}", response_model=schemas.NoteOut)
def put_note(note_id: str, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    updated = crud.update_note(db, note_id, note.area, note.title, note.body)
    if not updated:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return updated


@app.delete("/notes/{note_id}")
def remove_note(note_id: str, db: Session = Depends(get_db)):
    ok = crud.delete_note(db, note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return {"deleted": True}


# ---------- RELATIONS ----------
@app.get("/relations", response_model=list[schemas.RelationOut])
def get_relations(db: Session = Depends(get_db)):
    return crud.list_relations(db)


# ---------- CHAT ----------
@app.post("/chat", response_model=schemas.ChatResponse)
async def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada no servidor")

    system_prompt = crud.build_system_prompt(db)
    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            res = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": 400,
                    "system": system_prompt,
                    "messages": messages,
                },
            )
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Não foi possível conectar à API da Anthropic")

    if res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Erro da API Anthropic: {res.text}")

    data = res.json()
    reply = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            reply += block.get("text", "")
    reply = reply.strip() or "Não recebi resposta. Tenta de novo."

    saved_note = None
    match = SAVE_REGEX.search(reply)
    if match:
        area, title, body = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
        saved_note = crud.upsert_note(db, area, title, body)
        reply = SAVE_REGEX.sub("", reply).strip()

    return schemas.ChatResponse(reply=reply, saved_note=saved_note)


@app.get("/health")
def health():
    return {"status": "ok"}
