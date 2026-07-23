"""Chunk model for text chunking."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """A chunk of text with metadata.

    This model represents a chunk of text with associated metadata
    for tracking its position in the original document.
    """

    chunk_index: int
    text: str
    start_character: int
    end_character: int
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<Chunk(index={self.chunk_index}, chars={self.start_character}-{self.end_character}, page={self.page_number})>"
