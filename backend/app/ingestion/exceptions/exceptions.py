"""Exceptions for file ingestion operations."""


class IngestionException(Exception):
    """Base exception for ingestion errors."""

    pass


class UnsupportedFileTypeException(IngestionException):
    """Raised when attempting to process an unsupported file type."""

    def __init__(self, file_type: str):
        self.file_type = file_type
        super().__init__(f"Unsupported file type: {file_type}")


class ExtractionFailedException(IngestionException):
    """Raised when file extraction fails."""

    def __init__(self, message: str):
        super().__init__(f"Extraction failed: {message}")


class ProcessorNotFoundException(IngestionException):
    """Raised when no processor is found for a file type."""

    def __init__(self, file_type: str):
        self.file_type = file_type
        super().__init__(f"No processor found for file type: {file_type}")
