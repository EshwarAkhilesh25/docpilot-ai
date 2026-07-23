"""Chat response model."""

from dataclasses import dataclass
from uuid import UUID

from app.chat.models.citation import Citation
from app.chat.models.source import Source


@dataclass
class ChatResponse:
    """Response from the chat service.

    This model contains the generated answer along with the sources
    and citations that were used to generate it.
    """

    answer: str
    sources: list[Source]
    citations: list[Citation] | None = None
    session_id: UUID | None = None

    def __repr__(self) -> str:
        return f"<ChatResponse(sources={len(self.sources)}, citations={len(self.citations) if self.citations else 0}, session_id={self.session_id})>"
