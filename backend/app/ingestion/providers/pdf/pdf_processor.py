"""PDF processor implementing FileProcessor interface."""

import logging
from pathlib import Path

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.models.extraction import ExtractionResult
from app.ingestion.providers.pdf.pdf_extractor import PDFTextExtractor
from app.models.enums import FileType

logger = logging.getLogger(__name__)


class PDFProcessor(FileProcessor):
    """Processor for PDF files.

    This processor validates PDF files and extracts text using PDFTextExtractor.
    It returns an ExtractionResult with the extracted text and metadata.
    """

    def __init__(self, extractor: PDFTextExtractor):
        """Initialize the PDF processor.

        Args:
            extractor: PDF text extractor instance.
        """
        self._extractor = extractor

    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports the given file type.

        Args:
            file_type: The file type to check.

        Returns:
            True if the file type is PDF, False otherwise.
        """
        return file_type == FileType.PDF

    async def process(self, file_path: Path) -> ExtractionResult:
        """Process a PDF file and extract text.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ExtractionResult containing extracted text and metadata.

        Raises:
            ExtractionFailedException: If processing fails.
        """
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                raise ExtractionFailedException(f"File not found: {file_path}")

            # Extract text using the extractor
            extraction_data = self._extractor.extract(str(file_path))

            # Create ExtractionResult
            result = ExtractionResult(
                raw_text=extraction_data["raw_text"],
                pages=extraction_data["pages"],
                metadata=extraction_data["metadata"],
                page_count=extraction_data.get("page_count"),
                character_count=extraction_data.get("character_count"),
                ocr_used=extraction_data.get("ocr_used", False),
            )

            pass

            return result

        except ExtractionFailedException:
            raise
        except Exception as e:
            pass
            raise ExtractionFailedException(f"PDF processing failed: {e}")
