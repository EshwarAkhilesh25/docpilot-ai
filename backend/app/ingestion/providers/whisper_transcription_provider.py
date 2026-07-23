"""Whisper transcription provider using Groq API."""

import logging
import time
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.models.extraction import ExtractionResult

logger = logging.getLogger(__name__)
settings = get_settings()


class WhisperTranscriptionProvider(TranscriptionProvider):
    """Whisper transcription provider using Groq API.

    This provider uses Groq's Whisper API for fast audio transcription.
    It maintains a single AsyncClient for all requests and supports graceful shutdown.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
    ):
        """Initialize the Whisper transcription provider.

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY from config.
            model: Model to use for transcription. If None, uses WHISPER_MODEL from config.
            timeout: Request timeout in seconds. If None, uses TRANSCRIPTION_TIMEOUT from config.
            max_retries: Maximum number of retries. If None, uses TRANSCRIPTION_MAX_RETRIES from config.
            retry_delay: Initial delay between retries. If None, uses TRANSCRIPTION_RETRY_DELAY from config.
        """
        self._api_key = api_key or settings.GROQ_API_KEY
        self._model = model or settings.WHISPER_MODEL
        self._timeout = timeout or settings.TRANSCRIPTION_TIMEOUT
        self._max_retries = max_retries or settings.TRANSCRIPTION_MAX_RETRIES
        self._retry_delay = retry_delay or settings.TRANSCRIPTION_RETRY_DELAY
        self._base_url = "https://api.groq.com/openai/v1"
        self._client: httpx.AsyncClient | None = None

        if not self._api_key:
            pass

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared AsyncClient.

        Returns:
            The shared AsyncClient instance.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        """Close the AsyncClient gracefully.

        This should be called during application shutdown.
        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes client."""
        await self.close()

    async def transcribe(self, file_path: Path) -> ExtractionResult:
        """Transcribe an audio file.

        Args:
            file_path: Path to the audio file to transcribe.

        Returns:
            ExtractionResult containing transcribed text and metadata.

        Raises:
            ExtractionFailedException: If transcription fails.
        """
        if not self._api_key:
            raise ExtractionFailedException("GROQ_API_KEY not configured for transcription")

        # Validate file exists
        if not file_path.exists():
            raise ExtractionFailedException(f"Audio file not found: {file_path}")

        time.time()

        try:
            # Read file (audio or video)
            with open(file_path, "rb") as media_file:
                media_data = media_file.read()

            # Determine file type and MIME type
            file_extension = file_path.suffix.lower()
            if file_extension == ".mp4":
                mime_type = "video/mp4"
                filename = "video.mp4"
            elif file_extension == ".mp3":
                mime_type = "audio/mpeg"
                filename = "audio.mp3"
            elif file_extension == ".wav":
                mime_type = "audio/wav"
                filename = "audio.wav"
            else:
                mime_type = "audio/mpeg"
                filename = "audio.mp3"

            # Call Groq Whisper API
            result = await self._call_api_with_retry(media_data, mime_type, filename)

            # Create ExtractionResult
            extraction_result = ExtractionResult(
                raw_text=result["text"],
                pages=[],  # Audio/video doesn't have pages
                metadata={
                    "transcription_model": self._model,
                    "file_size": len(media_data),
                    "file_type": file_extension,
                },
                page_count=None,  # Audio/video doesn't have pages
                character_count=len(result["text"]),
                duration=result.get("duration"),
                language=result.get("language"),
            )

            pass

            return extraction_result

        except ExtractionFailedException:
            raise
        except Exception as e:
            pass
            raise ExtractionFailedException(f"Transcription failed: {e}")

    async def _call_api_with_retry(self, media_data: bytes, mime_type: str, filename: str) -> dict:
        """Call Groq Whisper API with exponential backoff retry.

        Args:
            media_data: Media file data as bytes.
            mime_type: MIME type of the media file.
            filename: Filename to send to the API.

        Returns:
            Transcription result dictionary.

        Raises:
            ExtractionFailedException: If all retries fail.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        # Prepare multipart form data
        files = {
            "file": (filename, media_data, mime_type),
        }
        data = {
            "model": self._model,
            "response_format": "verbose_json",
            "timestamp_granularities": ["segment"],
        }

        last_error = None
        for attempt in range(self._max_retries):
            try:
                client = self._get_client()
                response = await client.post(
                    f"{self._base_url}/audio/transcriptions",
                    headers=headers,
                    data=data,
                    files=files,
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "text": result.get("text", ""),
                        "language": result.get("language"),
                        "duration": result.get("duration"),
                    }

                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = self._retry_delay * (2**attempt)
                    pass
                    import asyncio

                    await asyncio.sleep(wait_time)
                    continue

                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                    raise ExtractionFailedException(
                        f"Groq API error (status {response.status_code}): {error_msg}"
                    )

            except httpx.TimeoutException as e:
                last_error = ExtractionFailedException(f"Groq API timeout: {e}")
                pass
                import asyncio

                await asyncio.sleep(self._retry_delay * (2**attempt))

            except httpx.HTTPError as e:
                last_error = ExtractionFailedException(f"Groq API HTTP error: {e}")
                pass
                import asyncio

                await asyncio.sleep(self._retry_delay * (2**attempt))

            except Exception as e:
                last_error = ExtractionFailedException(f"Unexpected error: {e}")
                pass
                break

        # All retries failed
        raise last_error or ExtractionFailedException("Failed to transcribe after retries")
