from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class BookmarkCreate(BaseModel):
    location: int = Field(default=0, ge=0)
    label: str | None = Field(default=None, max_length=255)
    note: str | None = None


class BookmarkOut(BaseModel):
    id: int
    chapter_id: int
    location: int
    label: str | None
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
