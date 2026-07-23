"""Internal models for file ingestion results."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedText:
    """Raw extracted text from a file."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TextChunk:
    """A chunk of text for processing (e.g., for embeddings)."""

    index: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of file extraction processing."""

    raw_text: str
    pages: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    page_count: int | None = None
    character_count: int | None = None
    duration: float | None = None  # For audio/video in seconds
    language: str | None = None
    ocr_used: bool | None = None
