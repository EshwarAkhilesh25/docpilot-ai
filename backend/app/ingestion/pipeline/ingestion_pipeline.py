"""Pipeline for file ingestion processing."""

from pathlib import Path

from app.ingestion.exceptions import UnsupportedFileTypeException
from app.ingestion.factory.processor_factory import ProcessorFactory
from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.interfaces.text_normalizer import TextNormalizer
from app.ingestion.models import ExtractionResult
from app.models.enums import FileType


class IngestionPipeline:
    """Pipeline for ingesting and processing uploaded files.

    This pipeline orchestrates the file ingestion process by:
    1. Receiving a document
    2. Resolving the appropriate processor
    3. Extracting text
    4. Normalizing text (optional)
    5. Returning the extraction result

    The pipeline is designed to be extensible - new processing stages
    can be added without modifying existing code.
    """

    def __init__(
        self,
        processor_factory: ProcessorFactory,
        text_normalizer: TextNormalizer | None = None,
    ) -> None:
        """Initialize the ingestion pipeline.

        Args:
            processor_factory: Factory for resolving file processors.
            text_normalizer: Optional normalizer for text preprocessing.
        """
        self._processor_factory = processor_factory
        self._text_normalizer = text_normalizer

    async def process(self, file_path: Path, file_type: FileType) -> ExtractionResult:
        """Process a file through the ingestion pipeline.

        Args:
            file_path: Path to the file to process.
            file_type: The FileType enum value.

        Returns:
            ExtractionResult containing extracted text and metadata.

        Raises:
            UnsupportedFileTypeException: If no processor supports the file type.
            ExtractionFailedException: If extraction fails.
        """
        # Resolve processor for file type
        processor = self._resolve_processor(file_type)

        # Extract text using the processor
        result = await processor.process(file_path)

        # Normalize text if normalizer is provided
        if self._text_normalizer is not None:
            result = self._text_normalizer.normalize(result)

        return result

    def _resolve_processor(self, file_type: FileType) -> FileProcessor:
        """Resolve the appropriate processor for the file type.

        Args:
            file_type: The FileType enum value.

        Returns:
            The FileProcessor instance for the file type.

        Raises:
            UnsupportedFileTypeException: If no processor supports the file type.
        """
        if not self._processor_factory.supports(file_type):
            raise UnsupportedFileTypeException(file_type.value)

        return self._processor_factory.get_processor(file_type)
