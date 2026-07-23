"""Citation model for chat responses."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Citation:
    """Citation information for a chat response.

    This model represents a specific retrieved chunk that was used
    as a citation for generating the chat response. Unlike Source,
    Citation represents the exact chunk with its similarity score.
    """

    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    page_number: int | None = None
    similarity_score: float = 0.0

    def __repr__(self) -> str:
        return f"<Citation(doc_id={self.document_id}, chunk_idx={self.chunk_index}, page={self.page_number}, score={self.similarity_score:.4f})>"
