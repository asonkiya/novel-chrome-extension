from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.chapter import Chapter


def create_chapter(
    db: Session,
    *,
    novel_id: int,
    chapter_no: int,
    title: str | None = None,
    raw: str | None = None,
    content: str | None = None,
    source_url: str | None = None,
    status: str = "raw_only",
) -> Chapter:
    ch = Chapter(
        novel_id=novel_id,
        chapter_no=chapter_no,
        title=title,
        raw=raw,
        content=content,
        source_url=source_url,
        status=status,
    )
    db.add(ch)
    db.flush()
    return ch


def get_chapter(db: Session, chapter_id: int) -> Chapter | None:
    return db.get(Chapter, chapter_id)


def get_chapter_by_no(db: Session, novel_id: int, chapter_no: int) -> Chapter | None:
    return (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel_id, Chapter.chapter_no == chapter_no)
        .first()
    )


def list_chapters(db: Session, novel_id: int, limit: int = 500, offset: int = 0) -> list[Chapter]:
    return (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel_id)
        .order_by(Chapter.chapter_no.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_chapter(
    db: Session,
    chapter: Chapter,
    *,
    title: str | None = None,
    raw: str | None = None,
    content: str | None = None,
    source_url: str | None = None,
    status: str | None = None,
) -> Chapter:
    if title is not None:
        chapter.title = title
    if raw is not None:
        chapter.raw = raw
    if content is not None:
        chapter.content = content
    if source_url is not None:
        chapter.source_url = source_url
    if status is not None:
        chapter.status = status
    db.flush()
    return chapter


def set_translation(
    db: Session,
    chapter: Chapter,
    *,
    content: str,
    translated_at: datetime | None = None,
    status: str = "translated",
) -> Chapter:
    chapter.content = content
    chapter.status = status
    chapter.translated_at = translated_at or datetime.utcnow()
    db.flush()
    return chapter


def set_links(
    db: Session,
    chapter: Chapter,
    *,
    prev_chapter_id: int | None = None,
    next_chapter_id: int | None = None,
) -> Chapter:
    chapter.prev_chapter_id = prev_chapter_id
    chapter.next_chapter_id = next_chapter_id
    db.flush()
    return chapter


def delete_chapter(db: Session, ch: Chapter) -> None:
    db.delete(ch)
