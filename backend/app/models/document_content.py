from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.document import Document


"""DocumentContent model for storing extracted document content."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class DocumentContent(BaseModel):
    """DocumentContent model representing extracted content from documents.

    This model stores the raw text and metadata extracted from documents
    during the processing pipeline. It has a one-to-one relationship with Document.
    """

    __tablename__ = "document_contents"

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    page_count: Mapped[int | None] = mapped_column(nullable=True)
    character_count: Mapped[int | None] = mapped_column(nullable=True)
    content_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # One-to-one with Document
    document: Mapped[Document] = relationship("Document", back_populates="content", uselist=False)

    def __repr__(self) -> str:
        return f"<DocumentContent(id={self.id}, document_id={self.document_id}, language={self.language})>"
