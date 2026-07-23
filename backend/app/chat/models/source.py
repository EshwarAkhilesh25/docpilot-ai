"""Source model for chat responses."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Source:
    """Source information for a chat response.

    This model represents a document chunk that was used as a source
    for generating the chat response.
    """

    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    start_page: int | None = None
    end_page: int | None = None
    similarity_score: float = 0.0

    def __repr__(self) -> str:
        return f"<Source(doc_id={self.document_id}, chunk_idx={self.chunk_index}, score={self.similarity_score:.4f})>"
