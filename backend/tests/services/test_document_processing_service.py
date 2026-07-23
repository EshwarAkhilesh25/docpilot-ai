"""Tests for DocumentProcessingService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.document_content import DocumentContent
from app.models.enums import FileType
from app.services.document_processing_service import DocumentProcessingServiceImpl
from app.services.exceptions import DocumentProcessingException


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    # Let AsyncMock handle the async context manager automatically, but ensure it returns itself
    uow.__aenter__.return_value = uow
    return uow


@pytest.fixture
def mock_uow_factory(mock_uow):
    """Fixture for mocked UoW factory."""
    factory = MagicMock(return_value=mock_uow)
    return factory


@pytest.fixture
def mock_extraction_service():
    """Fixture for mocked ExtractionService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_chunking_service():
    """Fixture for mocked ChunkingService."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_embedding_service():
    """Fixture for mocked EmbeddingService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_vector_index_service():
    """Fixture for mocked VectorIndexService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_llm_provider():
    """Fixture for mocked LLM provider."""
    provider = AsyncMock()
    return provider


@pytest.fixture
def mock_document():
    """Fixture for mocked Document."""
    document = MagicMock()
    document.id = uuid4()
    document.file_type = FileType.PDF
    document.storage_path = "test/path.pdf"
    return document


@pytest.fixture
def mock_document_content():
    """Fixture for mocked DocumentContent."""
    content = MagicMock(spec=DocumentContent)
    content.id = uuid4()
    content.raw_text = "This is the extracted document text."
    content.summary = None
    return content


class TestSummarizeDocument:
    """Tests for summarize_document method."""

    @pytest.mark.asyncio
    async def test_summarize_document_success(
        self,
        mock_uow_factory,
        mock_uow,
        mock_llm_provider,
        mock_document_content,
    ):
        """Test successful document summarization."""
        # Setup
        document_id = uuid4()
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )
        mock_llm_provider.generate_summary = AsyncMock(return_value="This is a summary.")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.summarize_document(document_id)

        # Assert
        mock_llm_provider.generate_summary.assert_called_once_with(mock_document_content.raw_text)
        mock_uow.document_content_repository.update_summary.assert_called_once_with(
            document_id, "This is a summary."
        )
        mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_document_already_exists(
        self,
        mock_uow_factory,
        mock_uow,
        mock_llm_provider,
        mock_document_content,
    ):
        """Test summarization when summary already exists (idempotent)."""
        # Setup
        document_id = uuid4()
        mock_document_content.summary = "Existing summary."
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.summarize_document(document_id)

        # Assert - LLM should not be called if summary exists
        mock_llm_provider.generate_summary.assert_not_called()
        mock_uow.document_content_repository.update_summary.assert_not_called()

    @pytest.mark.asyncio
    async def test_summarize_document_no_llm_provider(
        self,
        mock_uow_factory,
        mock_uow,
    ):
        """Test summarization when LLM provider is not configured."""
        # Setup
        document_id = uuid4()

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute - should not raise, just log and return
        await service.summarize_document(document_id)

        # Assert - no repository calls
        mock_uow.document_content_repository.get_by_document_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_summarize_document_no_content(
        self,
        mock_uow_factory,
        mock_uow,
        mock_llm_provider,
    ):
        """Test summarization when document content is not found."""
        # Setup
        document_id = uuid4()
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(return_value=None)
        mock_llm_provider.generate_summary = AsyncMock(return_value="Summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute & Assert
        with pytest.raises(DocumentProcessingException) as exc_info:
            await service.summarize_document(document_id)

        assert "content not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_summarize_document_no_raw_text(
        self,
        mock_uow_factory,
        mock_uow,
        mock_llm_provider,
        mock_document_content,
    ):
        """Test summarization when raw text is not available."""
        # Setup
        document_id = uuid4()
        mock_document_content.raw_text = None
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )
        mock_llm_provider.generate_summary = AsyncMock(return_value="Summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute & Assert
        with pytest.raises(DocumentProcessingException) as exc_info:
            await service.summarize_document(document_id)

        assert "content not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_summarize_document_llm_failure(
        self,
        mock_uow_factory,
        mock_uow,
        mock_llm_provider,
        mock_document_content,
    ):
        """Test summarization when LLM fails."""
        # Setup
        document_id = uuid4()
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )
        mock_llm_provider.generate_summary = AsyncMock(side_effect=Exception("LLM error"))

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=AsyncMock(),
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute & Assert
        with pytest.raises(DocumentProcessingException) as exc_info:
            await service.summarize_document(document_id)

        assert "Summarization failed" in str(exc_info.value)


class TestDocumentProcessingService:
    """Tests for DocumentProcessingServiceImpl."""

    def test_init(
        self,
        mock_uow_factory,
        mock_extraction_service,
        mock_chunking_service,
        mock_embedding_service,
        mock_vector_index_service,
    ):
        """Test service initialization."""
        service = DocumentProcessingServiceImpl(
            mock_uow_factory,
            mock_extraction_service,
            mock_chunking_service,
            mock_embedding_service,
            mock_vector_index_service,
        )
        assert service._uow_factory is mock_uow_factory
        assert service._extraction_service is mock_extraction_service
        assert service._chunking_service is mock_chunking_service
        assert service._embedding_service is mock_embedding_service
        assert service._vector_index_service is mock_vector_index_service

    @pytest.mark.asyncio
    async def test_process_with_summarization(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_embedding_service,
        mock_vector_index_service,
        mock_llm_provider,
        mock_document,
        mock_document_content,
    ):
        """Test full processing pipeline with summarization."""
        # Setup
        document_id = uuid4()
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        mock_uow.document_chunk_repository.list_by_document = AsyncMock(
            side_effect=[
                [],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
            ]
        )

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        mock_llm_provider.generate_summary = AsyncMock(return_value="Summary")

        service = DocumentProcessingServiceImpl(
            mock_uow_factory,
            mock_extraction_service,
            mock_chunking_service,
            mock_embedding_service,
            mock_vector_index_service,
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.process(document_id)

        # Assert - summarization was called
        mock_llm_provider.generate_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_without_summarization(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_embedding_service,
        mock_vector_index_service,
        mock_document,
        mock_document_content,
    ):
        """Test full processing pipeline without LLM provider."""
        # Setup
        document_id = uuid4()
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            return_value=mock_document_content
        )

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        mock_uow.document_chunk_repository.list_by_document = AsyncMock(
            side_effect=[
                [],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
            ]
        )

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        service = DocumentProcessingServiceImpl(
            mock_uow_factory,
            mock_extraction_service,
            mock_chunking_service,
            mock_embedding_service,
            mock_vector_index_service,
            llm_provider=None,
        )

        # Execute - should not raise
        await service.process(document_id)

        # Assert - processing continues without summarization
        assert True  # If we get here, no exception was raised


class TestAudioProcessing:
    """Tests for audio file processing through the pipeline."""

    @pytest.mark.asyncio
    async def test_extract_audio_success(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_document,
        mock_document_content,
    ):
        """Test successful audio extraction (transcription)."""
        # Setup
        document_id = uuid4()
        str(document_id)
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(return_value=None)

        # Mock extraction service to return transcription result
        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed audio text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=25,
                duration=120.5,
                language="en",
            )
        )

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute
        await service.extract_document(document_id)

        # Assert
        mock_extraction_service.extract.assert_called_once()
        mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_audio_transcription_failure(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_document,
    ):
        """Test handling of transcription failure."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(return_value=None)
        mock_extraction_service.extract = AsyncMock(side_effect=Exception("Transcription failed"))

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute & Assert
        with pytest.raises(DocumentProcessingException) as exc_info:
            await service.extract_document(document_id)

        assert "extraction failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_audio_summarization_after_transcription(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_llm_provider,
        mock_document,
        mock_document_content,
    ):
        """Test that summarization works after audio transcription."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=[
                None,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
            ]
        )
        mock_document_content.raw_text = "Transcribed audio text"

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed audio text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=25,
                duration=120.5,
                language="en",
            )
        )
        mock_llm_provider.generate_summary = AsyncMock(return_value="Audio summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.extract_document(document_id)
        await service.summarize_document(document_id)

        # Assert
        mock_llm_provider.generate_summary.assert_called_once_with("Transcribed audio text")

    @pytest.mark.asyncio
    async def test_audio_chunking_after_transcription(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_document,
        mock_document_content,
    ):
        """Test that chunking works after audio transcription."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=[
                None,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
                mock_document_content,
            ]
        )
        mock_document_content.raw_text = "Transcribed audio text"

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        mock_uow.document_chunk_repository.list_by_document = AsyncMock(
            side_effect=[
                [],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
                [mock_db_chunk],
            ]
        )

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed audio text for chunking",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=40,
                duration=120.5,
                language="en",
            )
        )

        # Mock chunk objects
        class MockChunk:
            def __init__(self, text):
                self.text = text
                self.chunk_index = 0
                self.page_number = None
                self.start_character = 0
                self.end_character = len(text)
                self.metadata = {}

        mock_chunking_service.chunk = MagicMock(
            return_value=[MockChunk("Chunk 1"), MockChunk("Chunk 2")]
        )

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=mock_chunking_service,
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute
        await service.extract_document(document_id)
        chunks = await service.chunk_document(document_id)

        # Assert
        assert len(chunks) == 2
        mock_chunking_service.chunk.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_audio_pipeline(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_embedding_service,
        mock_vector_index_service,
        mock_llm_provider,
        mock_document,
        mock_document_content,
    ):
        """Test complete audio processing pipeline: transcription → summarization → chunking → embeddings → indexing."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)

        def get_content_mock_audio(*args, **kwargs):
            if not getattr(get_content_mock_audio, "extracted", False):
                get_content_mock_audio.extracted = True
                return None
            return mock_document_content

        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=get_content_mock_audio
        )
        mock_document_content.raw_text = "Transcribed audio text"

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        def get_chunks_mock_audio(*args, **kwargs):
            get_chunks_mock_audio.calls += 1
            if get_chunks_mock_audio.calls == 1:
                return []
            return [mock_db_chunk]

        get_chunks_mock_audio.calls = 0
        mock_uow.document_chunk_repository.list_by_document = AsyncMock(
            side_effect=get_chunks_mock_audio
        )

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed audio text",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=25,
                duration=120.5,
                language="en",
            )
        )

        class MockChunk:
            def __init__(self, text):
                self.text = text
                self.chunk_index = 0
                self.page_number = None
                self.start_character = 0
                self.end_character = len(text)
                self.metadata = {}

        mock_chunking_service.chunk = MagicMock(return_value=[MockChunk("Chunk 1")])
        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
        mock_vector_index_service.count_vectors = AsyncMock(return_value=0)
        mock_llm_provider.generate_summary = AsyncMock(return_value="Audio summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=mock_chunking_service,
            embedding_service=mock_embedding_service,
            vector_index_service=mock_vector_index_service,
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.process(document_id)

        # Assert - all stages were called
        mock_extraction_service.extract.assert_called_once()
        mock_llm_provider.generate_summary.assert_called_once()
        mock_chunking_service.chunk.assert_called_once()
        mock_embedding_service.generate_embeddings.assert_called_once()
        mock_vector_index_service.index_vectors.assert_called_once()


class TestVideoProcessing:
    """Tests for video file processing through the pipeline."""

    @pytest.mark.asyncio
    async def test_extract_video_success(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_document,
        mock_document_content,
    ):
        """Test successful video extraction (transcription)."""
        # Setup
        document_id = uuid4()
        str(document_id)
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(return_value=None)

        # Mock extraction service to return transcription result
        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
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

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute
        await service.extract_document(document_id)

        # Assert
        mock_extraction_service.extract.assert_called_once()
        mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_video_transcription_failure(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_document,
    ):
        """Test handling of video transcription failure."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        mock_uow.document_content_repository.get_by_document_id = AsyncMock(return_value=None)
        mock_extraction_service.extract = AsyncMock(
            side_effect=Exception("Video transcription failed")
        )

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute & Assert
        with pytest.raises(DocumentProcessingException) as exc_info:
            await service.extract_document(document_id)

        assert "extraction failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_video_summarization_after_transcription(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_llm_provider,
        mock_document,
        mock_document_content,
    ):
        """Test that summarization works after video transcription."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)

        def get_content_mock_audio(*args, **kwargs):
            if not getattr(get_content_mock_audio, "extracted", False):
                get_content_mock_audio.extracted = True
                return None
            return mock_document_content

        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=get_content_mock_audio
        )
        mock_document_content.raw_text = "Transcribed video text"

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
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
        mock_llm_provider.generate_summary = AsyncMock(return_value="Video summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=MagicMock(),
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=mock_llm_provider,
        )

        # Execute
        await service.extract_document(document_id)
        await service.summarize_document(document_id)

        # Assert
        mock_llm_provider.generate_summary.assert_called_once_with("Transcribed video text")

    @pytest.mark.asyncio
    async def test_video_chunking_after_transcription(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_document,
        mock_document_content,
    ):
        """Test that chunking works after video transcription."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)

        def get_content_mock_audio(*args, **kwargs):
            if not getattr(get_content_mock_audio, "extracted", False):
                get_content_mock_audio.extracted = True
                return None
            return mock_document_content

        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=get_content_mock_audio
        )
        mock_document_content.raw_text = "Transcribed video text"

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        def get_chunks_mock_audio(*args, **kwargs):
            get_chunks_mock_audio.calls += 1
            if get_chunks_mock_audio.calls == 1:
                return []
            return [mock_db_chunk]

        get_chunks_mock_audio.calls = 0
        mock_uow.document_chunk_repository.list_by_document = AsyncMock(
            side_effect=get_chunks_mock_audio
        )

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
            return_value=ExtractionResult(
                raw_text="Transcribed video text for chunking",
                pages=[],
                metadata={"language": "en"},
                page_count=None,
                character_count=39,
                duration=180.5,
                language="en",
            )
        )

        # Mock chunk objects
        class MockChunk:
            def __init__(self, text):
                self.text = text
                self.chunk_index = 0
                self.page_number = None
                self.start_character = 0
                self.end_character = len(text)
                self.metadata = {}

        mock_chunking_service.chunk = MagicMock(
            return_value=[MockChunk("Chunk 1"), MockChunk("Chunk 2")]
        )

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=mock_chunking_service,
            embedding_service=AsyncMock(),
            vector_index_service=AsyncMock(),
            llm_provider=None,
        )

        # Execute
        await service.extract_document(document_id)
        chunks = await service.chunk_document(document_id)

        # Assert
        assert len(chunks) == 2
        mock_chunking_service.chunk.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_video_pipeline(
        self,
        mock_uow_factory,
        mock_uow,
        mock_extraction_service,
        mock_chunking_service,
        mock_embedding_service,
        mock_vector_index_service,
        mock_llm_provider,
        mock_document,
        mock_document_content,
    ):
        """Test complete video processing pipeline: transcription → summarization → chunking → embeddings → indexing."""
        # Setup
        document_id = uuid4()
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)

        def get_content_mock(*args, **kwargs):
            if not getattr(get_content_mock, "extracted", False):
                get_content_mock.extracted = True
                return None
            return mock_document_content

        mock_uow.document_content_repository.get_by_document_id = AsyncMock(
            side_effect=get_content_mock
        )
        mock_document_content.raw_text = "Transcribed video text"

        mock_chunk_obj = MagicMock()
        mock_chunk_obj.text = "test chunk"
        mock_chunk_obj.chunk_index = 0
        mock_chunk_obj.page_number = 1
        mock_chunk_obj.start_character = 0
        mock_chunk_obj.end_character = 10
        mock_chunk_obj.metadata = {}
        mock_chunking_service.chunk.return_value = [mock_chunk_obj]

        mock_db_chunk = MagicMock()
        mock_db_chunk.vector_id = "vec1"
        mock_db_chunk.text = "test chunk"
        mock_db_chunk.chunk_index = 0
        mock_db_chunk.chunk_metadata = {}

        def get_chunks_mock(*args, **kwargs):
            get_chunks_mock.calls += 1
            if get_chunks_mock.calls == 1:
                return []
            return [mock_db_chunk]

        get_chunks_mock.calls = 0
        mock_uow.document_chunk_repository.list_by_document = AsyncMock(side_effect=get_chunks_mock)

        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])

        from app.ingestion.models.extraction import ExtractionResult

        mock_extraction_service.extract = AsyncMock(
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

        class MockChunk:
            def __init__(self, text):
                self.text = text
                self.chunk_index = 0
                self.page_number = None
                self.start_character = 0
                self.end_character = len(text)
                self.metadata = {}

        mock_chunking_service.chunk = MagicMock(return_value=[MockChunk("Chunk 1")])
        mock_embedding_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
        mock_vector_index_service.count_vectors = AsyncMock(return_value=0)
        mock_llm_provider.generate_summary = AsyncMock(return_value="Video summary")

        service = DocumentProcessingServiceImpl(
            uow_factory=mock_uow_factory,
            extraction_service=mock_extraction_service,
            chunking_service=mock_chunking_service,
            embedding_service=mock_embedding_service,
            vector_index_service=mock_vector_index_service,
            llm_provider=mock_llm_provider,
        )

        # Execute

        await service.process(document_id)

        # Assert - all stages were called
        mock_extraction_service.extract.assert_called_once()
        mock_llm_provider.generate_summary.assert_called_once()
        mock_chunking_service.chunk.assert_called_once()
        mock_embedding_service.generate_embeddings.assert_called_once()
        mock_vector_index_service.index_vectors.assert_called_once()

        get_content_mock.extracted = False
        # Test PDF
        mock_document.file_type = FileType.PDF
        mock_uow.document_repository.get_by_id = AsyncMock(return_value=mock_document)
        await service.process(document_id)
        mock_uow.document_repository.get_by_id.assert_called_once()

        get_content_mock.extracted = False
        # Test AUDIO
        mock_document.file_type = FileType.AUDIO
        mock_uow.document_repository.get_by_id.reset_mock()
        await service.process(document_id)
        mock_uow.document_repository.get_by_id.assert_called_once()

        get_content_mock.extracted = False
        # Test VIDEO
        mock_document.file_type = FileType.VIDEO
        mock_uow.document_repository.get_by_id.reset_mock()
        await service.process(document_id)
        mock_uow.document_repository.get_by_id.assert_called_once()
