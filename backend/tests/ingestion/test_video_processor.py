"""Tests for VideoProcessor."""

from unittest.mock import AsyncMock

import pytest

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.models.extraction import ExtractionResult
from app.ingestion.providers.video.video_processor import VideoProcessor
from app.models.enums import FileType


@pytest.fixture
def mock_transcription_provider():
    """Fixture for mocked TranscriptionProvider."""
    provider = AsyncMock(spec=TranscriptionProvider)
    return provider


@pytest.fixture
def video_processor(mock_transcription_provider):
    """Fixture for VideoProcessor."""
    return VideoProcessor(mock_transcription_provider)


class TestVideoProcessor:
    """Tests for VideoProcessor."""

    def test_supports_video(self, video_processor):
        """Test that processor supports VIDEO file type."""
        assert video_processor.supports(FileType.VIDEO)

    def test_does_not_support_pdf(self, video_processor):
        """Test that processor does not support PDF."""
        assert not video_processor.supports(FileType.PDF)

    def test_does_not_support_audio(self, video_processor):
        """Test that processor does not support AUDIO."""
        assert not video_processor.supports(FileType.AUDIO)

    @pytest.mark.asyncio
    async def test_process_mp4_success(
        self, video_processor, mock_transcription_provider, tmp_path
    ):
        """Test successful MP4 processing."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_transcription_provider.transcribe = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed video text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=24,
                duration=180.5,
                language="en",
            )
        )

        # Execute
        result = await video_processor.process(str(video_file))

        # Assert
        assert result.raw_text == "Transcribed video text"
        assert result.language == "en"
        assert result.duration == 180.5
        assert result.page_count is None
        mock_transcription_provider.transcribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_file_not_found(self, video_processor):
        """Test processing when file does not exist."""
        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await video_processor.process("/nonexistent/video.mp4")

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_unsupported_format(self, video_processor, tmp_path):
        """Test processing with unsupported video format."""
        # Setup
        video_file = tmp_path / "test.avi"
        video_file.write_bytes(b"fake avi data")

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await video_processor.process(str(video_file))

        assert "unsupported" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_transcription_failure(
        self, video_processor, mock_transcription_provider, tmp_path
    ):
        """Test processing when transcription fails."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_transcription_provider.transcribe = AsyncMock(
            side_effect=ExtractionFailedException("Transcription failed")
        )

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await video_processor.process(str(video_file))

        assert "transcription failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_provider_error(
        self, video_processor, mock_transcription_provider, tmp_path
    ):
        """Test processing when provider raises unexpected error."""
        # Setup
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video data")

        mock_transcription_provider.transcribe = AsyncMock(side_effect=Exception("Provider error"))

        # Execute & Assert
        with pytest.raises(ExtractionFailedException) as exc_info:
            await video_processor.process(str(video_file))

        assert "processing failed" in str(exc_info.value).lower()
