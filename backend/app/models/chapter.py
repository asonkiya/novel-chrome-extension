from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True)

    novel_id: Mapped[int] = mapped_column(
        ForeignKey("novels.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Canonical ordering/display number (unique per novel)
    chapter_no: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # untranslated
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # translated

    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # Workflow state for reader/translation pipeline
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="raw_only")
    translated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Doubly linked list pointers
    prev_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )
    next_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Self-referential relationships
    prev_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter",
        foreign_keys=[prev_chapter_id],
        remote_side="Chapter.id",
        uselist=False,
        post_update=True,
    )
    next_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter",
        foreign_keys=[next_chapter_id],
        remote_side="Chapter.id",
        uselist=False,
        post_update=True,
    )

    novel: Mapped["Novel"] = relationship("Novel", back_populates="chapters")

    __table_args__ = (
        UniqueConstraint("novel_id", "chapter_no", name="uq_chapters_novel_chapter_no"),
        Index("ix_chapters_novel_chapter_no", "novel_id", "chapter_no"),
    )
