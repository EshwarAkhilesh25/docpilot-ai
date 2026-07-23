"""DOCX file processor."""

import logging
from pathlib import Path

from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.models import ExtractionResult
from app.ingestion.providers.docx.docx_extractor import DOCXTextExtractor
from app.models.enums import FileType

logger = logging.getLogger(__name__)


class DOCXProcessor(FileProcessor):
    """Processor for DOCX files.

    This processor orchestrates the extraction of text and metadata
    from DOCX files.
    """

    def __init__(self, extractor: DOCXTextExtractor) -> None:
        """Initialize the DOCX processor.

        Args:
            extractor: The DOCX text extractor instance.
        """
        self._extractor = extractor

    def supports(self, file_type: str) -> bool:
        """Check if this processor supports the given file type."""
        return file_type == FileType.DOCX

    async def process(self, file_path: Path) -> ExtractionResult:
        """Process a DOCX file to extract text and metadata.

        Args:
            file_path: Path to the DOCX file.

        Returns:
            ExtractionResult containing text and metadata.

        Raises:
            ExtractionFailedException: If processing fails.
        """
        pass

        extracted_text = await self._extractor.extract_text(file_path)

        # Add processor-specific metadata
        metadata = extracted_text.metadata.copy()
        metadata.update(
            {
                "file_type": FileType.DOCX.value,
                "processor": self.__class__.__name__,
            }
        )

        pass

        return ExtractionResult(
            raw_text=extracted_text.text,
            metadata=metadata,
        )
