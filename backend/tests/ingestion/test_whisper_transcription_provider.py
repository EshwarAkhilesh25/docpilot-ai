"""Tests for WhisperTranscriptionProvider."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.providers.whisper_transcription_provider import WhisperTranscriptionProvider


@pytest.fixture
def mock_client():
    """Fixture for mocked httpx AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.is_closed = False
    return client


@pytest.fixture
def provider(mock_client):
    """Fixture for WhisperTranscriptionProvider with mocked client."""
    with patch("app.ingestion.providers.whisper_transcription_provider.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_settings.WHISPER_MODEL = "whisper-large-v3"
        mock_settings.TRANSCRIPTION_TIMEOUT = 300.0
        mock_settings.TRANSCRIPTION_MAX_RETRIES = 3
        mock_settings.TRANSCRIPTION_RETRY_DELAY = 2.0
        provider = WhisperTranscriptionProvider()
        provider._client = mock_client
        return provider


class TestWhisperTranscriptionProvider:
    """Tests for WhisperTranscriptionProvider."""

    @pytest.mark.asyncio
    async def test_transcribe_success(self, provider, mock_client, tmp_path):
        """Test successful transcription."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "This is the transcribed text.",
            "language": "en",
            "duration": 120.5,
        }
        mock_client.post.return_value = mock_response

        # Execute
        result = await provider.transcribe(audio_file)

        # Assert
        assert result.raw_text == "This is the transcribed text."
        assert result.language == "en"
        assert result.duration == 120.5
        assert result.page_count is None
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcribe_retry_on_rate_limit(self, provider, mock_client, tmp_path):
        """Test retry on rate limit."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "text": "Transcribed text",
            "language": "en",
            "duration": 90.0,
        }
        mock_client.post.side_effect = [mock_response_429, mock_response_200]

        # Execute
        result = await provider.transcribe(audio_file)

        # Assert
        assert result.raw_text == "Transcribed text"
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_transcribe_timeout(self, provider, mock_client, tmp_path):
        """Test timeout handling."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(audio_file)

        assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcribe_http_error(self, provider, mock_client, tmp_path):
        """Test HTTP error handling."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        mock_client.post.side_effect = httpx.HTTPError("Connection error")

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(audio_file)

        assert "http error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcribe_api_error(self, provider, mock_client, tmp_path):
        """Test API error response."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal server error"}}
        mock_client.post.return_value = mock_response

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(audio_file)

        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_file_not_found(self, provider, tmp_path):
        """Test transcription when file does not exist."""
        # Setup
        audio_file = tmp_path / "nonexistent.mp3"

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(audio_file)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcribe_no_api_key(self, tmp_path):
        """Test error when API key is not configured."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        with patch(
            "app.ingestion.providers.whisper_transcription_provider.settings"
        ) as mock_settings:
            mock_settings.GROQ_API_KEY = None
            mock_settings.WHISPER_MODEL = "whisper-large-v3"
            mock_settings.TRANSCRIPTION_TIMEOUT = 300.0
            mock_settings.TRANSCRIPTION_MAX_RETRIES = 3
            mock_settings.TRANSCRIPTION_RETRY_DELAY = 2.0
            provider = WhisperTranscriptionProvider()

            # Execute & Assert
            with pytest.raises(ExtractionFailedException) as exc_info:
                await provider.transcribe(audio_file)

            assert "not configured" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcribe_custom_params(self, provider, mock_client, tmp_path):
        """Test transcription with custom parameters."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "Transcribed",
            "language": "en",
            "duration": 60.0,
        }
        mock_client.post.return_value = mock_response

        # Execute
        result = await provider.transcribe(audio_file)

        # Assert
        assert result.raw_text == "Transcribed"
        # Verify the call was made
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_client(self, provider, mock_client):
        """Test closing the AsyncClient."""
        # Execute
        await provider.close()

        # Assert
        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, tmp_path):
        """Test using provider as async context manager."""
        with patch(
            "app.ingestion.providers.whisper_transcription_provider.settings"
        ) as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.WHISPER_MODEL = "whisper-large-v3"
            mock_settings.TRANSCRIPTION_TIMEOUT = 300.0
            mock_settings.TRANSCRIPTION_MAX_RETRIES = 3
            mock_settings.TRANSCRIPTION_RETRY_DELAY = 2.0

            async with WhisperTranscriptionProvider() as provider:
                assert provider is not None
                assert provider._client is not None

    @pytest.mark.asyncio
    async def test_transcribe_mp4_success(self, provider, mock_client, tmp_path):
        """Test successful MP4 video transcription."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "This is the transcribed video text.",
            "language": "en",
            "duration": 180.5,
        }
        mock_client.post.return_value = mock_response

        # Execute
        result = await provider.transcribe(video_file)

        # Assert
        assert result.raw_text == "This is the transcribed video text."
        assert result.language == "en"
        assert result.duration == 180.5
        assert result.page_count is None
        mock_client.post.assert_called_once()
        # Verify the file was sent with video/mp4 MIME type
        call_args = mock_client.post.call_args
        files = call_args.kwargs.get("files", {})
        assert "file" in files
        assert files["file"][2] == "video/mp4"

    @pytest.mark.asyncio
    async def test_transcribe_mp4_retry_on_rate_limit(self, provider, mock_client, tmp_path):
        """Test retry on rate limit for MP4."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "text": "Transcribed video text",
            "language": "en",
            "duration": 150.0,
        }
        mock_client.post.side_effect = [mock_response_429, mock_response_200]

        # Execute
        result = await provider.transcribe(video_file)

        # Assert
        assert result.raw_text == "Transcribed video text"
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_transcribe_mp4_timeout(self, provider, mock_client, tmp_path):
        """Test timeout handling for MP4."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(video_file)

        assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcribe_mp4_provider_error(self, provider, mock_client, tmp_path):
        """Test provider error for MP4."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal server error"}}
        mock_client.post.return_value = mock_response

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await provider.transcribe(video_file)

        assert "500" in str(exc_info.value)
