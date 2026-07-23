"""Video processor implementing FileProcessor interface."""

import logging
from pathlib import Path

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.models.extraction import ExtractionResult
from app.models.enums import FileType

logger = logging.getLogger(__name__)


class VideoProcessor(FileProcessor):
    """Processor for video files.

    This processor validates video files and transcribes them using a TranscriptionProvider.
    It returns an ExtractionResult with the transcribed text and metadata.
    Supports MP4 format.
    """

    SUPPORTED_FORMATS = {FileType.VIDEO}  # VIDEO covers MP4

    def __init__(self, transcription_provider: TranscriptionProvider):
        """Initialize the video processor.

        Args:
            transcription_provider: Transcription provider instance.
        """
        self._transcription_provider = transcription_provider

    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports the given file type.

        Args:
            file_type: The file type to check.

        Returns:
            True if the file type is VIDEO, False otherwise.
        """
        return file_type in self.SUPPORTED_FORMATS

    async def process(self, file_path: Path) -> ExtractionResult:
        """Process a video file and transcribe it.

        Args:
            file_path: Path to the video file.

        Returns:
            ExtractionResult containing transcribed text and metadata.

        Raises:
            ExtractionFailedException: If processing fails.
        """
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                raise ExtractionFailedException(f"File not found: {file_path}")

            # Validate file extension
            if path.suffix.lower() not in {".mp4"}:
                raise ExtractionFailedException(
                    f"Unsupported video format: {path.suffix}. Supported formats: .mp4"
                )

            pass

            # Transcribe using the transcription provider
            result = await self._transcription_provider.transcribe(path)

            pass

            return result

        except ExtractionFailedException:
            raise
        except Exception as e:
            pass
            raise ExtractionFailedException(f"Video processing failed: {e}")
