from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.reading_progress import ReadingProgress
from app.models.bookmark import Bookmark


# -------- Reading Progress --------


def get_progress(db: Session, novel_id: int) -> ReadingProgress | None:
    return db.query(ReadingProgress).filter(ReadingProgress.novel_id == novel_id).first()


def upsert_progress(
    db: Session,
    *,
    novel_id: int,
    current_chapter_id: int | None,
    position: float,
) -> ReadingProgress:
    row = get_progress(db, novel_id)
    if row:
        row.current_chapter_id = current_chapter_id
        row.position = position
        db.flush()
        return row

    row = ReadingProgress(
        novel_id=novel_id,
        current_chapter_id=current_chapter_id,
        position=position,
    )
    db.add(row)
    db.flush()
    return row


# -------- Bookmarks --------


def create_bookmark(
    db: Session,
    *,
    chapter_id: int,
    location: int = 0,
    label: str | None = None,
    note: str | None = None,
) -> Bookmark:
    bm = Bookmark(
        chapter_id=chapter_id,
        location=location,
        label=label,
        note=note,
    )
    db.add(bm)
    db.flush()
    return bm


def list_bookmarks_for_chapter(db: Session, chapter_id: int) -> list[Bookmark]:
    return (
        db.query(Bookmark)
        .filter(Bookmark.chapter_id == chapter_id)
        .order_by(Bookmark.created_at.asc(), Bookmark.id.asc())
        .all()
    )


def get_bookmark(db: Session, bookmark_id: int) -> Bookmark | None:
    return db.get(Bookmark, bookmark_id)


def delete_bookmark(db: Session, bookmark: Bookmark) -> None:
    db.delete(bookmark)
    db.flush()
