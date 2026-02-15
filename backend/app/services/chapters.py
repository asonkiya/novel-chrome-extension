from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.chapter import Chapter
from app.repos import chapter as chapter_repo


def rebuild_links_from_chapter_no(db: Session, novel_id: int) -> list[Chapter]:
    """
    Rebuilds prev/next pointers for all chapters of a novel using chapter_no ordering.
    This is your "fix everything" button if links ever get corrupted.
    """
    chapters = chapter_repo.list_chapters(db, novel_id=novel_id, limit=10_000, offset=0)

    # Clear pointers first
    for ch in chapters:
        ch.prev_chapter_id = None
        ch.next_chapter_id = None

    # Re-link by order
    for i, ch in enumerate(chapters):
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        ch.prev_chapter_id = prev_ch.id if prev_ch else None
        ch.next_chapter_id = next_ch.id if next_ch else None

    db.flush()
    return chapters


def insert_chapter_and_link(
    db: Session,
    *,
    novel_id: int,
    chapter_no: int,
    title: str | None = None,
    raw: str | None = None,
    content: str | None = None,
    source_url: str | None = None,
) -> Chapter:
    """
    Creates a chapter and inserts it into the doubly linked list based on chapter_no.

    Rules:
    - chapter_no is canonical ordering.
    - prev/next pointers are updated on neighbors to keep list consistent.
    """
    # Create the new chapter row first
    new_ch = chapter_repo.create_chapter(
        db,
        novel_id=novel_id,
        chapter_no=chapter_no,
        title=title,
        raw=raw,
        content=content,
        source_url=source_url,
        status="translated" if content else "raw_only",
    )

    # Find immediate neighbors by chapter_no
    # Previous = max chapter_no < new
    prev_ch = (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel_id, Chapter.chapter_no < chapter_no)
        .order_by(Chapter.chapter_no.desc())
        .first()
    )
    # Next = min chapter_no > new
    next_ch = (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel_id, Chapter.chapter_no > chapter_no)
        .order_by(Chapter.chapter_no.asc())
        .first()
    )

    # Link new chapter
    new_ch.prev_chapter_id = prev_ch.id if prev_ch else None
    new_ch.next_chapter_id = next_ch.id if next_ch else None

    # Update neighbors to point to new chapter
    if prev_ch:
        prev_ch.next_chapter_id = new_ch.id
    if next_ch:
        next_ch.prev_chapter_id = new_ch.id

    db.flush()
    return new_ch


def delete_chapter_and_relink(db: Session, *, chapter_id: int) -> Chapter:
    """
    Deletes a chapter and relinks its neighbors to keep the doubly linked list consistent.

    - prev.next -> deleted.next
    - next.prev -> deleted.prev
    """
    ch = chapter_repo.get_chapter(db, chapter_id)
    if not ch:
        raise ValueError("Chapter not found")

    # Load neighbors (if present)
    prev_ch = chapter_repo.get_chapter(db, ch.prev_chapter_id) if ch.prev_chapter_id else None
    next_ch = chapter_repo.get_chapter(db, ch.next_chapter_id) if ch.next_chapter_id else None

    # Relink neighbors around the deleted chapter
    if prev_ch:
        prev_ch.next_chapter_id = next_ch.id if next_ch else None
    if next_ch:
        next_ch.prev_chapter_id = prev_ch.id if prev_ch else None

    # Delete the chapter itself
    chapter_repo.delete_chapter(db, ch)

    db.flush()
    return ch


def delete_chapter_for_novel_and_relink(db: Session, *, novel_id: int, chapter_id: int):
    ch = chapter_repo.get_chapter(db, chapter_id)
    if not ch or ch.novel_id != novel_id:
        raise ValueError("Chapter not found for this novel")
    return delete_chapter_and_relink(db, chapter_id=chapter_id)
