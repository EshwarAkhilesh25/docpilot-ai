from abc import ABC, abstractmethod
from pathlib import Path

from app.ingestion.models import ExtractionResult
from app.models.enums import FileType


class FileProcessor(ABC):
    """Abstract interface for file processors.

    A FileProcessor is responsible for processing a specific file type
    and extracting structured data from it. Implementations should be
    file-type specific (e.g., PDFProcessor, AudioProcessor).
    """

    @abstractmethod
    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports the given file type.

        Args:
            file_type: The file extension (e.g., '.pdf', '.mp3').

        Returns:
            True if this processor can handle the file type, False otherwise.
        """
        pass

    @abstractmethod
    async def process(self, file_path: Path) -> ExtractionResult:
        """Process a file and extract its content.

        Args:
            file_path: Path to the file to process.

        Returns:
            ExtractionResult containing extracted text and metadata.

        Raises:
            ExtractionFailedException: If extraction fails.
        """
        pass
