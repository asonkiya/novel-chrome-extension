from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ReadingProgressUpsert(BaseModel):
    current_chapter_id: int | None = None
    position: float = Field(default=0.0, ge=0.0, le=1.0)


class ReadingProgressOut(BaseModel):
    id: int
    novel_id: int
    current_chapter_id: int | None
    position: float
    updated_at: datetime

    model_config = {"from_attributes": True}
