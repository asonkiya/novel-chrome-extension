from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.novel import Novel
from app.models.chapter import Chapter


def delete_novel_cascade(db: Session, *, novel_id: int) -> Novel:
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError("Novel not found")

    # delete chapters first (unless you have FK cascade configured)
    db.query(Chapter).filter(Chapter.novel_id == novel_id).delete(synchronize_session=False)

    db.delete(novel)
    db.flush()
    return novel


def delete_all_chapters_for_novel(db: Session, *, novel_id: int) -> int:
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError("Novel not found")

    deleted = (
        db.query(Chapter).filter(Chapter.novel_id == novel_id).delete(synchronize_session=False)
    )
    db.flush()
    return int(deleted)


def delete_chapters_by_no_range(
    db: Session,
    *,
    novel_id: int,
    start_no: int,
    end_no: int,
) -> int:
    """
    Deletes chapters with chapter_no between [start_no, end_no].
    Returns count deleted.
    """
    if start_no > end_no:
        start_no, end_no = end_no, start_no

    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError("Novel not found")

    deleted = (
        db.query(Chapter)
        .filter(
            Chapter.novel_id == novel_id,
            Chapter.chapter_no >= start_no,
            Chapter.chapter_no <= end_no,
        )
        .delete(synchronize_session=False)
    )
    db.flush()
    return int(deleted)
