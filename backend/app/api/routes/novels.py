from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repos import novel as novel_repo
from app.schemas import NovelContextUpdate, NovelCreate, NovelOut
from app.services.chapters import rebuild_links_from_chapter_no
from app.services.novels import (
    delete_all_chapters_for_novel,
    delete_chapters_by_no_range,
    delete_novel_cascade,
)

router = APIRouter(prefix="/novels", tags=["novels"])


@router.post("", response_model=NovelOut)
def create_novel(payload: NovelCreate, db: Session = Depends(get_db)):
    existing = novel_repo.get_novel_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=409, detail="Novel with this name already exists")

    n = novel_repo.create_novel(
        db, name=payload.name, source_lang=payload.source_lang, target_lang=payload.target_lang
    )
    db.commit()
    db.refresh(n)
    return n


@router.get("", response_model=list[NovelOut])
def list_novels(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return novel_repo.list_novels(db, limit=limit, offset=offset)


@router.get("/{novel_id}", response_model=NovelOut)
def get_novel(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")
    return n


@router.get("/{novel_id}/context")
def get_context(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")
    return n.context_json or {}


@router.put("/{novel_id}/context")
def put_context(novel_id: int, payload: NovelContextUpdate, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    novel_repo.set_context(db, n, payload.context_json)
    db.commit()
    return {"ok": True}


@router.delete("/{novel_id}")
def delete_novel(novel_id: int, db: Session = Depends(get_db)):
    try:
        deleted = delete_novel_cascade(db, novel_id=novel_id)
        db.commit()
        return {"ok": True, "deleted_novel_id": deleted.id, "name": deleted.name}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{novel_id}/chapters")
def delete_all_chapters(
    novel_id: int,
    db: Session = Depends(get_db),
    rebuild: bool = Query(
        False,
        description="Rebuild prev/next pointers after delete (mostly irrelevant if all deleted).",
    ),
):
    try:
        count = delete_all_chapters_for_novel(db, novel_id=novel_id)
        if rebuild:
            rebuild_links_from_chapter_no(db, novel_id=novel_id)
        db.commit()
        return {"ok": True, "deleted": count}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{novel_id}/chapters/by-no-range")
def delete_chapters_range(
    novel_id: int,
    start: int = Query(..., description="Start chapter_no (inclusive)"),
    end: int = Query(..., description="End chapter_no (inclusive)"),
    db: Session = Depends(get_db),
    rebuild: bool = Query(
        True, description="Rebuild prev/next pointers from chapter_no after delete"
    ),
):
    try:
        count = delete_chapters_by_no_range(db, novel_id=novel_id, start_no=start, end_no=end)

        if rebuild:
            rebuild_links_from_chapter_no(db, novel_id=novel_id)

        db.commit()
        return {"ok": True, "deleted": count, "range": {"start": start, "end": end}}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
