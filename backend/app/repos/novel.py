from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark
from app.models.chapter import Chapter
from app.models.novel import Novel
from app.models.reading_progress import ReadingProgress


def create_novel(db: Session, name: str, source_lang: str = "ko", target_lang: str = "en") -> Novel:
    novel = Novel(name=name, source_lang=source_lang, target_lang=target_lang)
    db.add(novel)
    db.flush()  # assigns novel.id
    return novel


def get_novel(db: Session, novel_id: int) -> Novel | None:
    return db.get(Novel, novel_id)


def get_novel_by_name(db: Session, name: str) -> Novel | None:
    return db.query(Novel).filter(Novel.name == name).first()


def list_novels(db: Session, limit: int = 100, offset: int = 0) -> list[Novel]:
    return db.query(Novel).order_by(Novel.id.asc()).offset(offset).limit(limit).all()


def update_novel(
    db: Session,
    novel: Novel,
    *,
    name: str | None = None,
    source_lang: str | None = None,
    target_lang: str | None = None,
) -> Novel:
    if name is not None:
        novel.name = name
    if source_lang is not None:
        novel.source_lang = source_lang
    if target_lang is not None:
        novel.target_lang = target_lang
    db.flush()
    return novel


def set_context(db: Session, novel: Novel, context_json: dict) -> Novel:
    novel.context_json = context_json
    db.flush()
    return novel
