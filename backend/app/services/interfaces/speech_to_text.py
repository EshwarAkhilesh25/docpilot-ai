from abc import ABC, abstractmethod
from io import BytesIO


class SpeechToTextProvider(ABC):
    """Abstract provider interface for speech-to-text operations.

    This interface defines the contract for audio transcription across
    different providers (OpenAI Whisper, Google Speech-to-Text, etc.).
    Implementations should handle backend-specific details while adhering
    to this interface.
    """

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_data: BytesIO,
        language: str | None = None,
        timestamp_granularities: list[str] | None = None,
    ) -> dict:
        """Transcribe audio to text.

        Args:
            audio_data: The audio file content as a BytesIO object.
            language: Optional language code (e.g., 'en', 'es'). None for auto-detection.
            timestamp_granularities: Optional list of timestamp granularities
                                    (e.g., ['word', 'segment']).

        Returns:
            A dictionary containing:
            - text: The transcribed text.
            - segments: List of transcribed segments with timestamps (if requested).
            - language: Detected language code.

        Raises:
            TranscriptionError: If transcription fails.
        """

    @abstractmethod
    async def get_supported_languages(self) -> list[str]:
        """Get the list of supported languages.

        Returns:
            A list of language codes supported by the provider.
        """

    @abstractmethod
    async def get_audio_duration(self, audio_data: BytesIO) -> float:
        """Get the duration of an audio file in seconds.

        Args:
            audio_data: The audio file content as a BytesIO object.

        Returns:
            The duration of the audio in seconds.

        Raises:
            TranscriptionError: If duration calculation fails.
        """
