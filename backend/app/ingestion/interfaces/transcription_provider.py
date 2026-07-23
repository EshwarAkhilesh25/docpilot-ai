"""Interface for transcription providers."""

from abc import ABC, abstractmethod
from pathlib import Path

from app.ingestion.models.extraction import ExtractionResult


class TranscriptionProvider(ABC):
    """Abstract interface for audio transcription providers.

    This interface defines the contract for transcribing audio files.
    Implementations can use different providers (Whisper, Deepgram, Azure Speech, etc.).
    """

    @abstractmethod
    async def transcribe(self, file_path: Path) -> ExtractionResult:
        """Transcribe an audio file.

        Args:
            file_path: Path to the audio file to transcribe.

        Returns:
            ExtractionResult containing transcribed text and metadata.

        Raises:
            TranscriptionFailedException: If transcription fails.
        """
        pass
