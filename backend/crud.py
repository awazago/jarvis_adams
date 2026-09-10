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


def create_note(db: Session, area: str, title: str, body: str, auto_link: bool = True) -> models.Note:
    note = models.Note(id=f"n_{uuid.uuid4().hex[:10]}", area=area, title=title, body=body)
    db.add(note)
    db.commit()
    db.refresh(note)
    if auto_link:
        auto_connect(db, note)
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


def link_notes(db: Session, id_a: str, id_b: str):
    """Cria uma relação entre duas notas, evitando duplicata em qualquer ordem."""
    if not id_a or not id_b or id_a == id_b:
        return
    exists = db.query(models.Relation).filter(
        ((models.Relation.note_a == id_a) & (models.Relation.note_b == id_b)) |
        ((models.Relation.note_a == id_b) & (models.Relation.note_b == id_a))
    ).first()
    if exists:
        return
    db.add(models.Relation(id=f"r_{uuid.uuid4().hex[:10]}", note_a=id_a, note_b=id_b))
    db.commit()


def auto_connect(db: Session, note: models.Note):
    """Garante que toda nota nova nasça conectada — nunca órfã no grafo."""
    core = db.query(models.Note).filter(models.Note.area == "meta", models.Note.id != note.id).first()
    if core:
        link_notes(db, note.id, core.id)
    siblings = (
        db.query(models.Note)
        .filter(models.Note.area == note.area, models.Note.id != note.id)
        .order_by(models.Note.created_at.desc())
        .limit(2)
        .all()
    )
    for s in siblings:
        link_notes(db, note.id, s.id)


def upsert_note(db: Session, area: str, title: str, body: str, link_titles: list[str] | None = None) -> models.Note:
    """Usado pelo protocolo [[SAVE:...]] — cria ou atualiza por título (case-insensitive).
    Se o Jarvis indicou conexões via [[LINK:...]], liga a essas notas existentes;
    senão, aplica conectividade automática (núcleo + notas recentes da mesma área)."""
    if area not in AREAS:
        area = "meta"
    existing = find_note_by_title(db, title)
    if existing:
        existing.area = area
        existing.body = body
        db.commit()
        db.refresh(existing)
        note, is_new = existing, False
    else:
        note, is_new = create_note(db, area, title, body, auto_link=False), True

    linked_any = False
    if link_titles:
        for lt in link_titles:
            target = find_note_by_title(db, lt)
            if target and target.id != note.id:
                link_notes(db, note.id, target.id)
                linked_any = True

    if is_new and not linked_any:
        auto_connect(db, note)

    return note


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

Se {JARVIS['address']} revelar algo novo e duradouro sobre a vida dele durante a conversa, termine sua resposta com uma linha no formato EXATO [[SAVE:area|titulo|texto]] (area deve ser uma de: metas, trabalho, projetos, financas, aprendizado, saude, relacoes, meta). Se já existir uma nota com esse título, ela deve ser atualizada; senão nasce uma nova. Inclua essa linha SOMENTE quando houver algo realmente novo — nunca repita a cada resposta.

Se essa nota nova ou atualizada se conecta de verdade com alguma nota que já existe no Second Brain acima (mesmo projeto, mesma pessoa, causa e efeito, mesmo objetivo maior, etc.), adicione UMA linha extra pra CADA conexão que você perceber, logo depois do SAVE, no formato EXATO [[LINK:titulo_da_nota_nova|titulo_da_nota_existente]] — use exatamente o mesmo título usado no SAVE do lado esquerdo. Pense como um analista: não force conexão fraca só por existir, mas também não deixe de conectar o que realmente se relaciona. Isso é o que mantém o Second Brain vivo, com uma teia de verdade entre os assuntos — não notas soltas."""
