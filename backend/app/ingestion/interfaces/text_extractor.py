from abc import ABC, abstractmethod
from pathlib import Path

from app.ingestion.models import ExtractionResult


class TextExtractor(ABC):
    """Abstract interface for text extractors.

    A TextExtractor is responsible for extracting raw text from a file.
    This is a lower-level interface that FileProcessor implementations
    can compose to handle the actual extraction logic.
    """

    @abstractmethod
    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract text from a file.

        Args:
            file_path: Path to the file to extract text from.

        Returns:
            ExtractionResult containing the extracted text and basic metadata.

        Raises:
            ExtractionFailedException: If extraction fails.
        """
        pass
