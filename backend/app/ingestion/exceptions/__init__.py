"""Exceptions for file ingestion."""

from app.ingestion.exceptions.exceptions import (
    ExtractionFailedException,
    ProcessorNotFoundException,
    UnsupportedFileTypeException,
)

__all__ = [
    "UnsupportedFileTypeException",
    "ExtractionFailedException",
    "ProcessorNotFoundException",
]
