from pathlib import Path

from app.models.enums import FileType

"""Service for document text extraction."""

import logging

from app.ingestion.models.extraction import ExtractionResult
from app.ingestion.pipeline.ingestion_pipeline import IngestionPipeline
from app.services.exceptions import DocumentProcessingException

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting text from documents.

    This service coordinates the extraction of text from uploaded documents
    using the ingestion pipeline. It handles PDF extraction and returns
    structured extraction results.
    """

    def __init__(self, ingestion_pipeline: IngestionPipeline):
        """Initialize the extraction service.

        Args:
            ingestion_pipeline: Ingestion pipeline for document processing.
        """
        self._ingestion_pipeline = ingestion_pipeline

    async def extract(self, file_path: str, file_type: str) -> ExtractionResult:
        """Extract text from a document.

        Args:
            file_path: Path to the document file.
            file_type: Type of the document (e.g., 'pdf').

        Returns:
            ExtractionResult containing extracted text and metadata.

        Raises:
            DocumentProcessingException: If extraction fails.
        """
        try:
            pass

            result = await self._ingestion_pipeline.process(
                file_path=Path(file_path),
                file_type=FileType(file_type),
            )

            pass

            return result

        except Exception as e:
            pass
            raise DocumentProcessingException(f"Extraction failed: {e}")
