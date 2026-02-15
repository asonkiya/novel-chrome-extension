from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NovelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_lang: str = Field(default="ko", min_length=2, max_length=20)
    target_lang: str = Field(default="en", min_length=2, max_length=20)


class NovelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_lang: str | None = Field(default=None, min_length=2, max_length=20)
    target_lang: str | None = Field(default=None, min_length=2, max_length=20)


class NovelContextUpdate(BaseModel):
    context_json: dict[str, Any] = Field(default_factory=dict)


class NovelOut(BaseModel):
    id: int
    name: str
    source_lang: str
    target_lang: str
    context_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
