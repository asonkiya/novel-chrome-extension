from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.chapter import Chapter

_SENTENCE_SPLIT_RE = re.compile(r"([.!?])\s+")


def format_translated_chapter(db: Session, *, chapter_id: int) -> Chapter:
    ch = db.get(Chapter, chapter_id)
    if not ch:
        raise ValueError("Chapter not found")

    if not ch.content or not ch.content.strip():
        raise ValueError("Chapter has no translated content. Translate first.")

    src = ch.content.strip()

    src = re.sub(r"\r\n?", "\n", src)
    src = re.sub(r"[ \t]+", " ", src)
    src = re.sub(r"\n{3,}", "\n\n", src).strip()

    chunks = _SENTENCE_SPLIT_RE.split(src)

    parts: list[str] = []

    for i in range(0, len(chunks) - 1, 2):
        sentence = (chunks[i] + chunks[i + 1]).strip()
        if sentence:
            parts.append(sentence)

    if len(chunks) % 2 != 0:
        last = chunks[-1].strip()
        if last:
            parts.append(last)

    formatted = "\n\n".join(parts).strip()

    formatted = re.sub(r"\n{3,}", "\n\n", formatted)

    formatted += "\n"

    ch.content = formatted

    if hasattr(ch, "updated_at"):
        ch.updated_at = datetime.now(timezone.utc)

    db.flush()
    return ch
