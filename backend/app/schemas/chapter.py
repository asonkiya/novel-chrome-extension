from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ChapterCreate(BaseModel):
    chapter_no: int = Field(ge=1)
    title: str | None = Field(default=None, max_length=500)
    raw: str | None = None
    content: str | None = None
    source_url: str | None = Field(default=None, max_length=2048)


class ChapterUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    raw: str | None = None
    content: str | None = None
    source_url: str | None = Field(default=None, max_length=2048)
    status: str | None = Field(default=None, max_length=30)


class ChapterOut(BaseModel):
    id: int
    novel_id: int
    chapter_no: int
    title: str | None
    raw: str | None
    content: str | None
    source_url: str | None
    status: str
    translated_at: datetime | None
    created_at: datetime
    updated_at: datetime

    prev_chapter_id: int | None
    next_chapter_id: int | None

    model_config = {"from_attributes": True}


class ChapterListItem(BaseModel):
    id: int
    chapter_no: int
    title: str | None
    status: str
    prev_chapter_id: int | None
    next_chapter_id: int | None

    model_config = {"from_attributes": True}
