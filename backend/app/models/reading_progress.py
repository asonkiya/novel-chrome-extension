from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id: Mapped[int] = mapped_column(primary_key=True)

    novel_id: Mapped[int] = mapped_column(
        ForeignKey("novels.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    current_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )

    # 0.0 - 1.0 scroll progress (or reinterpret later as offset)
    position: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    novel: Mapped["Novel"] = relationship("Novel", back_populates="reading_progress")
    current_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter", foreign_keys=[current_chapter_id]
    )

    __table_args__ = (
        UniqueConstraint("novel_id", name="uq_reading_progress_novel_id"),
    )
