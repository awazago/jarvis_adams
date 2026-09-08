import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from config import JARVIS, AREAS

AREA_LABELS = {
    "metas": "Metas",
    "trabalho": "Carreira",
    "projetos": "Projetos",
    "financas": "Finanças",
    "aprendizado": "Aprendizado",
    "saude": "Saúde",
    "relacoes": "Relações",
    "meta": "Você",
}


def list_notes(db: Session):
    return db.query(models.Note).order_by(models.Note.created_at).all()


def list_relations(db: Session):
    return db.query(models.Relation).all()


def create_note(db: Session, area: str, title: str, body: str) -> models.Note:
    note = models.Note(id=f"n_{uuid.uuid4().hex[:10]}", area=area, title=title, body=body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note_id: str, area: str | None, title: str | None, body: str | None):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        return None
    if area is not None:
        note.area = area
    if title is not None:
        note.title = title
    if body is not None:
        note.body = body
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: str) -> bool:
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        return False
    db.query(models.Relation).filter(
        (models.Relation.note_a == note_id) | (models.Relation.note_b == note_id)
    ).delete()
    db.delete(note)
    db.commit()
    return True


def find_note_by_title(db: Session, title: str) -> models.Note | None:
    return db.query(models.Note).filter(func.lower(models.Note.title) == title.lower()).first()


def upsert_note(db: Session, area: str, title: str, body: str) -> models.Note:
    """Usado pelo protocolo [[SAVE:...]] — cria ou atualiza por título (case-insensitive)."""
    if area not in AREAS:
        area = "meta"
    existing = find_note_by_title(db, title)
    if existing:
        existing.area = area
        existing.body = body
        db.commit()
        db.refresh(existing)
        return existing
    return create_note(db, area, title, body)


def build_system_prompt(db: Session) -> str:
    notes = list_notes(db)
    blocks = []
    for area in AREAS:
        items = [n for n in notes if n.area == area]
        if not items:
            continue
        lines = "\n".join(f"- {n.title}: {n.body}" for n in items)
        blocks.append(f"## {AREA_LABELS[area]}\n{lines}")
    brain = "\n\n".join(blocks)

    return f"""Você é {JARVIS['name']}, um assistente de voz pessoal para {JARVIS['address']}. Sua personalidade é: {JARVIS['persona']}. Trate-o sempre como "{JARVIS['address']}".
Responda SEMPRE em português do Brasil, em 2 a 4 frases curtas, faladas, sem emojis e sem markdown.
Você conhece profundamente a vida de {JARVIS['address']} através do Second Brain abaixo — use esse contexto pra personalizar toda resposta, sendo direto, analítico e com uma pitada de sarcasmo quando fizer sentido.

SECOND BRAIN:
{brain}

Se {JARVIS['address']} revelar algo novo e duradouro sobre a vida dele durante a conversa, termine sua resposta com uma linha no formato EXATO [[SAVE:area|titulo|texto]] (area deve ser uma de: metas, trabalho, projetos, financas, aprendizado, saude, relacoes, meta). Se já existir uma nota com esse título, ela deve ser atualizada; senão nasce uma nova. Inclua essa linha SOMENTE quando houver algo realmente novo — nunca repita a cada resposta."""
