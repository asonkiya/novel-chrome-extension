from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.chapter import Chapter
from app.repos import novel as novel_repo

router = APIRouter(prefix="/novels", tags=["export"])


def _chapters_in_order(db: Session, novel_id: int) -> list[Chapter]:
    return (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel_id)
        .order_by(Chapter.chapter_no.asc())
        .all()
    )


@router.get("/{novel_id}/export.json")
def export_novel_json(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    chapters = _chapters_in_order(db, novel_id)
    payload = {
        "novel": {
            "id": n.id,
            "name": n.name,
            "source_lang": n.source_lang,
            "target_lang": n.target_lang,
            "created_at": getattr(n, "created_at", None),
            "updated_at": getattr(n, "updated_at", None),
        },
        "chapters": [
            {
                "id": ch.id,
                "chapter_no": ch.chapter_no,
                "title": ch.title,
                "source_url": ch.source_url,
                "status": ch.status,
                "text": (ch.content or ch.raw or ""),
            }
            for ch in chapters
        ],
    }
    return JSONResponse(content=payload)


@router.get("/{novel_id}/export.md", response_class=PlainTextResponse)
def export_novel_markdown(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    chapters = _chapters_in_order(db, novel_id)

    parts: list[str] = [f"# {n.name}\n"]
    for ch in chapters:
        title = ch.title or f"Chapter {ch.chapter_no}"
        text = (ch.content or ch.raw or "").strip()
        parts.append(f"## {ch.chapter_no}. {title}\n\n{text}\n")

    return "\n".join(parts)


@router.get("/{novel_id}/export.txt", response_class=PlainTextResponse)
def export_novel_text(novel_id: int, db: Session = Depends(get_db)):
    n = novel_repo.get_novel(db, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="Novel not found")

    chapters = _chapters_in_order(db, novel_id)

    parts: list[str] = [n.name, ""]
    for ch in chapters:
        title = ch.title or f"Chapter {ch.chapter_no}"
        text = (ch.content or ch.raw or "").strip()
        parts.append(f"{ch.chapter_no}. {title}")
        parts.append(text)
        parts.append("")  # spacer

    return "\n".join(parts)
