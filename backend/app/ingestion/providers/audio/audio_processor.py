"""Audio processor implementing FileProcessor interface."""

import logging
from pathlib import Path

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.file_processor import FileProcessor
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.models.extraction import ExtractionResult
from app.models.enums import FileType

logger = logging.getLogger(__name__)


class AudioProcessor(FileProcessor):
    """Processor for audio files.

    This processor validates audio files and transcribes them using a TranscriptionProvider.
    It returns an ExtractionResult with the transcribed text and metadata.
    Supports MP3 and WAV formats.
    """

    SUPPORTED_FORMATS = {FileType.AUDIO}  # AUDIO covers both MP3 and WAV

    def __init__(self, transcription_provider: TranscriptionProvider):
        """Initialize the audio processor.

        Args:
            transcription_provider: Transcription provider instance.
        """
        self._transcription_provider = transcription_provider

    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports the given file type.

        Args:
            file_type: The file type to check.

        Returns:
            True if the file type is AUDIO, False otherwise.
        """
        return file_type in self.SUPPORTED_FORMATS

    async def process(self, file_path: Path) -> ExtractionResult:
        """Process an audio file and transcribe it.

        Args:
            file_path: Path to the audio file.

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
            if path.suffix.lower() not in {".mp3", ".wav"}:
                raise ExtractionFailedException(
                    f"Unsupported audio format: {path.suffix}. Supported formats: .mp3, .wav"
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
            raise ExtractionFailedException(f"Audio processing failed: {e}")
