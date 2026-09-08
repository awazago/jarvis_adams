from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True)
    area = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Relation(Base):
    __tablename__ = "relations"

    id = Column(String, primary_key=True)
    note_a = Column(String, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    note_b = Column(String, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
