"""Tests for AudioProcessor."""

from unittest.mock import AsyncMock

import pytest

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.models.extraction import ExtractionResult
from app.ingestion.providers.audio.audio_processor import AudioProcessor
from app.models.enums import FileType


@pytest.fixture
def mock_transcription_provider():
    """Fixture for mocked TranscriptionProvider."""
    provider = AsyncMock(spec=TranscriptionProvider)
    return provider


@pytest.fixture
def audio_processor(mock_transcription_provider):
    """Fixture for AudioProcessor."""
    return AudioProcessor(mock_transcription_provider)


class TestAudioProcessor:
    """Tests for AudioProcessor."""

    def test_supports_audio(self, audio_processor):
        """Test that processor supports AUDIO file type."""
        assert audio_processor.supports(FileType.AUDIO)

    def test_does_not_support_pdf(self, audio_processor):
        """Test that processor does not support PDF."""
        assert not audio_processor.supports(FileType.PDF)

    @pytest.mark.asyncio
    async def test_process_mp3_success(
        self, audio_processor, mock_transcription_provider, tmp_path
    ):
        """Test successful MP3 processing."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_transcription_provider.transcribe = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=16,
                duration=120.5,
                language="en",
            )
        )

        # Execute
        result = await audio_processor.process(str(audio_file))

        # Assert
        assert result.raw_text == "Transcribed text"
        assert result.language == "en"
        assert result.duration == 120.5
        assert result.page_count is None
        mock_transcription_provider.transcribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_wav_success(
        self, audio_processor, mock_transcription_provider, tmp_path
    ):
        """Test successful WAV processing."""
        # Setup
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake wav data")

        mock_transcription_provider.transcribe = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed WAV text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=20,
                duration=90.0,
                language="en",
            )
        )

        # Execute
        result = await audio_processor.process(str(audio_file))

        # Assert
        assert result.raw_text == "Transcribed WAV text"
        mock_transcription_provider.transcribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_file_not_found(self, audio_processor):
        """Test processing when file does not exist."""
        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await audio_processor.process("/nonexistent/audio.mp3")

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_unsupported_format(self, audio_processor, tmp_path):
        """Test processing with unsupported audio format."""
        # Setup
        audio_file = tmp_path / "test.ogg"
        audio_file.write_bytes(b"fake ogg data")

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await audio_processor.process(str(audio_file))

        assert "unsupported" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_transcription_failure(
        self, audio_processor, mock_transcription_provider, tmp_path
    ):
        """Test processing when transcription fails."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_transcription_provider.transcribe = AsyncMock(
            side_effect=ExtractionFailedException("Transcription failed")
        )

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await audio_processor.process(str(audio_file))

        assert "transcription failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_provider_error(
        self, audio_processor, mock_transcription_provider, tmp_path
    ):
        """Test processing when provider raises unexpected error."""
        # Setup
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_transcription_provider.transcribe = AsyncMock(side_effect=Exception("Provider error"))

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await audio_processor.process(str(audio_file))

        assert "processing failed" in str(exc_info.value).lower()
