"""Internal models for file ingestion."""

from app.ingestion.models.extraction import ExtractedText, ExtractionResult, TextChunk

__all__ = [
    "ExtractionResult",
    "TextChunk",
    "ExtractedText",
]
