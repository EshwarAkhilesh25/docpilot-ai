"""Factory for creating file processors based on file type."""

from app.ingestion.exceptions import ProcessorNotFoundException
from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.providers.audio.audio_processor import AudioProcessor
from app.ingestion.providers.docx.docx_extractor import DOCXTextExtractor
from app.ingestion.providers.docx.docx_processor import DOCXProcessor
from app.ingestion.providers.pdf.pdf_extractor import PDFTextExtractor
from app.ingestion.providers.pdf.pdf_processor import PDFProcessor
from app.ingestion.providers.video.video_processor import VideoProcessor
from app.models.enums import FileType


class ProcessorFactory:
    """Factory for creating appropriate FileProcessor instances.

    This factory uses dependency injection to provide processors for
    different file types. New processors can be registered without
    modifying the factory code.
    """

    def __init__(self, transcription_provider: TranscriptionProvider | None = None) -> None:
        """Initialize the processor factory with empty registry.

        Args:
            transcription_provider: Optional transcription provider for audio/video files.
        """
        self._processors: dict[FileType, FileProcessor] = {}
        # Register built-in processors
        self._register_default_processors(transcription_provider)

    def _register_default_processors(
        self, transcription_provider: TranscriptionProvider | None
    ) -> None:
        """Register default processors for supported file types."""
        pdf_extractor = PDFTextExtractor()
        pdf_processor = PDFProcessor(pdf_extractor)
        self.register(FileType.PDF, pdf_processor)

        docx_extractor = DOCXTextExtractor()
        docx_processor = DOCXProcessor(docx_extractor)
        self.register(FileType.DOCX, docx_processor)

        # Register audio and video processors if transcription provider is available
        if transcription_provider:
            audio_processor = AudioProcessor(transcription_provider)
            self.register(FileType.AUDIO, audio_processor)

            video_processor = VideoProcessor(transcription_provider)
            self.register(FileType.VIDEO, video_processor)

    def register(self, file_type: FileType, processor: FileProcessor) -> None:
        """Register a processor for a specific file type.

        Args:
            file_type: The FileType enum value.
            processor: The processor instance to register.
        """
        self._processors[file_type] = processor

    def get_processor(self, file_type: FileType) -> FileProcessor:
        """Get a processor for the given file type.

        Args:
            file_type: The FileType enum value.

        Returns:
            The FileProcessor instance for the file type.

        Raises:
            ProcessorNotFoundException: If no processor is registered for the file type.
        """
        processor = self._processors.get(file_type)
        if processor is None:
            raise ProcessorNotFoundException(file_type.value)
        return processor

    def supports(self, file_type: FileType) -> bool:
        """Check if a processor exists for the given file type.

        Args:
            file_type: The FileType enum value.

        Returns:
            True if a processor is registered, False otherwise.
        """
        return file_type in self._processors
