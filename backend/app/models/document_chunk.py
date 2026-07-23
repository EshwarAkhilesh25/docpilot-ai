from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.document import Document


from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class DocumentChunk(BaseModel):
    """DocumentChunk model representing text chunks from documents."""

    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_character: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_character: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_timestamp: Mapped[float | None] = mapped_column(Integer, nullable=True)
    end_timestamp: Mapped[float | None] = mapped_column(Integer, nullable=True)
    vector_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    vector_index: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    chunk_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
