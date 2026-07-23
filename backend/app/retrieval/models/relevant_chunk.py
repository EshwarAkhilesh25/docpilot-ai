"""Relevant chunk model for retrieval results."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class RelevantChunk:
    """A retrieved document chunk with relevance information.

    This model represents a chunk that was retrieved during semantic search,
    containing the chunk data along with its similarity score and metadata.
    """

    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    text: str
    similarity_score: float
    start_page: int | None = None
    end_page: int | None = None
    metadata: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return f"<RelevantChunk(doc_id={self.document_id}, chunk_idx={self.chunk_index}, score={self.similarity_score:.4f})>"
