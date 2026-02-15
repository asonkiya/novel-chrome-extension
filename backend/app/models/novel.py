from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Novel(Base):
    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    source_lang: Mapped[str] = mapped_column(String(20), nullable=False, default="ko")
    target_lang: Mapped[str] = mapped_column(String(20), nullable=False, default="en")

    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="novel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Chapter.chapter_no",
    )

    reading_progress: Mapped[Optional["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="novel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
