from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repos import chapter as chapter_repo
from app.repos import novel as novel_repo
from app.schemas import ChapterCreate, ChapterListItem, ChapterOut, ChapterUpdate
from app.services.chapters import (
    delete_chapter_and_relink,
    delete_chapter_for_novel_and_relink,
    insert_chapter_and_link,
    rebuild_links_from_chapter_no,
)
from app.services.translation import translate_chapter

router = APIRouter(tags=["chapters"])


@router.post("/novels/{novel_id}/chapters", response_model=ChapterOut)
def create_chapter(novel_id: int, payload: ChapterCreate, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    existing = chapter_repo.get_chapter_by_no(db, novel_id=novel_id, chapter_no=payload.chapter_no)
    if existing:
        raise HTTPException(status_code=409, detail="Chapter number already exists for this novel")

    ch = insert_chapter_and_link(
        db,
        novel_id=novel_id,
        chapter_no=payload.chapter_no,
        title=payload.title,
        raw=payload.raw,
        content=payload.content,
        source_url=payload.source_url,
    )
    db.commit()
    db.refresh(ch)
    return ch


@router.get("/novels/{novel_id}/chapters", response_model=list[ChapterListItem])
def list_chapters(novel_id: int, db: Session = Depends(get_db), limit: int = 500, offset: int = 0):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")
    return chapter_repo.list_chapters(db, novel_id=novel_id, limit=limit, offset=offset)


@router.get("/novels/{novel_id}/chapters/{chapter_no}", response_model=ChapterOut)
def get_chapter_by_no(novel_id: int, chapter_no: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    ch = chapter_repo.get_chapter_by_no(db, novel_id=novel_id, chapter_no=chapter_no)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ch


@router.patch("/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(chapter_id: int, payload: ChapterUpdate, db: Session = Depends(get_db)):
    ch = chapter_repo.get_chapter(db, chapter_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_repo.update_chapter(
        db,
        ch,
        title=payload.title,
        raw=payload.raw,
        content=payload.content,
        source_url=payload.source_url,
        status=payload.status,
    )
    db.commit()
    db.refresh(ch)
    return ch


@router.post("/chapters/{chapter_id}/translate", response_model=ChapterOut)
def translate_one(chapter_id: int, db: Session = Depends(get_db)):
    ch = chapter_repo.get_chapter(db, chapter_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")

    try:
        updated = translate_chapter(db, novel_id=ch.novel_id, chapter_id=ch.id)
        db.commit()
        db.refresh(updated)
        return updated
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novels/{novel_id}/chapters/rebuild-links")
def rebuild_links(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    chapters = rebuild_links_from_chapter_no(db, novel_id=novel_id)
    db.commit()
    return {"ok": True, "count": len(chapters)}


@router.delete("/chapters/{chapter_id}", response_model=ChapterOut)
def delete_chapter(
    chapter_id: int,
    rebuild: bool = Query(
        False, description="If true, rebuild prev/next pointers from chapter_no after delete."
    ),
    db: Session = Depends(get_db),
):
    try:
        deleted = delete_chapter_and_relink(db, chapter_id=chapter_id)

        if rebuild:
            rebuild_links_from_chapter_no(db, novel_id=deleted.novel_id)

        db.commit()
        return deleted
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        db.rollback()
        raise


from fastapi import Query


@router.delete("/novels/{novel_id}/chapters/{chapter_id}", response_model=ChapterOut)
def delete_chapter_scoped(
    novel_id: int,
    chapter_id: int,
    db: Session = Depends(get_db),
    rebuild: bool = Query(
        False, description="If true, rebuild prev/next pointers from chapter_no after delete."
    ),
):
    # ensure novel exists (matches your style)
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    try:
        deleted = delete_chapter_for_novel_and_relink(db, novel_id=novel_id, chapter_id=chapter_id)

        if rebuild:
            rebuild_links_from_chapter_no(db, novel_id=novel_id)

        db.commit()
        db.refresh(deleted)
        return deleted
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
