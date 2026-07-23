"""Tests for DocumentProcessingWorker with stage-based orchestration."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.jobs.exceptions import JobExecutionException
from app.jobs.workers.document_processing_worker import DocumentProcessingWorker
from app.models.enums import ProcessingStage, ProcessingStatus


@pytest.fixture
def mock_uow_factory():
    """Fixture for mocked UnitOfWork factory."""
    factory = MagicMock()
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    factory.return_value = uow
    return factory, uow


@pytest.fixture
def mock_processing_service():
    """Fixture for mocked DocumentProcessingService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_processing_job():
    """Fixture for mocked ProcessingJob."""
    job = MagicMock()
    job.id = uuid4()
    job.status = ProcessingStatus.UPLOADED
    job.current_stage = ProcessingStage.UPLOADED
    job.progress = 0
    job.retry_count = 0
    job.error_message = None
    return job


class TestDocumentProcessingWorker:
    """Tests for DocumentProcessingWorker with stage-based orchestration."""

    def test_init(self, mock_uow_factory, mock_processing_service):
        """Test worker initialization."""
        factory, _ = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        assert worker._uow_factory is factory
        assert worker._processing_service is mock_processing_service

    @pytest.mark.asyncio
    async def test_process_full_pipeline_success(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test successful full pipeline from UPLOADED stage."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup
        mock_processing_job.current_stage = ProcessingStage.UPLOADED
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - all stage methods should be called
        mock_processing_service.extract_document.assert_called_once_with(document_id)
        mock_processing_service.chunk_document.assert_called()
        mock_processing_service.generate_embeddings.assert_called()
        mock_processing_service.index_vectors.assert_called()

        # Assert - stage transitions
        assert (
            uow.processing_job_repository.update_stage.call_count == 4
        )  # EXTRACTING, CHUNKING, EMBEDDING, INDEXING
        assert uow.processing_job_repository.update_heartbeat.call_count == 4  # Before each stage

        # Assert - final status
        final_update = uow.processing_job_repository.update.call_args_list[-1]
        final_job = final_update[0][0]
        assert final_job.status == ProcessingStatus.COMPLETED
        assert final_job.current_stage == ProcessingStage.COMPLETED

    @pytest.mark.asyncio
    async def test_resume_from_chunking(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test resume from CHUNKING stage (extraction already done)."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - job is at CHUNKING stage
        mock_processing_job.current_stage = ProcessingStage.CHUNKING
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - extraction should NOT be called (already done)
        mock_processing_service.extract_document.assert_not_called()

        # Assert - chunking and later stages should be called
        mock_processing_service.chunk_document.assert_called()
        mock_processing_service.generate_embeddings.assert_called()
        mock_processing_service.index_vectors.assert_called()

        # Assert - stage transitions (starting from CHUNKING)
        assert (
            uow.processing_job_repository.update_stage.call_count == 3
        )  # CHUNKING, EMBEDDING, INDEXING

    @pytest.mark.asyncio
    async def test_resume_from_embedding(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test resume from EMBEDDING stage (extraction and chunking already done)."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - job is at EMBEDDING stage
        mock_processing_job.current_stage = ProcessingStage.EMBEDDING
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - extraction and chunking should NOT be called
        mock_processing_service.extract_document.assert_not_called()
        mock_processing_service.chunk_document.assert_called()  # Called to get chunks for embedding

        # Assert - embedding and indexing should be called
        mock_processing_service.generate_embeddings.assert_called()
        mock_processing_service.index_vectors.assert_called()

        # Assert - stage transitions (starting from EMBEDDING)
        assert uow.processing_job_repository.update_stage.call_count == 2  # EMBEDDING, INDEXING

    @pytest.mark.asyncio
    async def test_resume_from_indexing(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test resume from INDEXING stage (extraction, chunking, embedding already done)."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - job is at INDEXING stage
        mock_processing_job.current_stage = ProcessingStage.INDEXING
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - only indexing should be called
        mock_processing_service.extract_document.assert_not_called()
        mock_processing_service.chunk_document.assert_called()  # Called to get chunks
        mock_processing_service.generate_embeddings.assert_called()  # Called to get embeddings
        mock_processing_service.index_vectors.assert_called_once()

        # Assert - stage transitions (starting from INDEXING)
        assert uow.processing_job_repository.update_stage.call_count == 1  # INDEXING only

    @pytest.mark.asyncio
    async def test_stage_failure_with_retry_increment(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test that stage failure increments retry count and marks as FAILED."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - extraction fails
        mock_processing_job.current_stage = ProcessingStage.UPLOADED
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)
        uow.processing_job_repository.increment_retry = AsyncMock()
        uow.processing_job_repository.mark_failed = AsyncMock()

        mock_processing_service.extract_document = AsyncMock(
            side_effect=Exception("Extraction failed")
        )

        # Execute
        with pytest.raises(JobExecutionException):
            await worker.process(document_id)

        # Assert - retry should be incremented and job marked as failed
        uow.processing_job_repository.increment_retry.assert_called_once_with(
            mock_processing_job.id
        )
        uow.processing_job_repository.mark_failed.assert_called_once_with(
            mock_processing_job.id, "Extraction failed: Extraction failed"
        )

    @pytest.mark.asyncio
    async def test_heartbeat_updates_before_each_stage(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test that heartbeat is updated before each stage."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup
        mock_processing_job.current_stage = ProcessingStage.UPLOADED
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - heartbeat should be called before each of 4 stages
        assert uow.processing_job_repository.update_heartbeat.call_count == 4
        for call in uow.processing_job_repository.update_heartbeat.call_args_list:
            assert call[0][0] == mock_processing_job.id

    @pytest.mark.asyncio
    async def test_no_job_found(self, mock_uow_factory, mock_processing_service):
        """Test processing when no job is found."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - no jobs returned
        uow.processing_job_repository.list_by_document = AsyncMock(return_value=[])

        # Execute & Assert
        with pytest.raises(JobExecutionException) as exc_info:
            await worker.process(document_id)

        assert "No processing job found" in str(exc_info.value)
        mock_processing_service.extract_document.assert_not_called()

    @pytest.mark.asyncio
    async def test_already_processing_status(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test that job already in PROCESSING status continues from current_stage."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup - job already in PROCESSING status at CHUNKING stage
        mock_processing_job.status = ProcessingStatus.PROCESSING
        mock_processing_job.current_stage = ProcessingStage.CHUNKING
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - should resume from CHUNKING, not restart
        mock_processing_service.extract_document.assert_not_called()
        mock_processing_service.chunk_document.assert_called()

    @pytest.mark.asyncio
    async def test_progress_updates_per_stage(
        self, mock_uow_factory, mock_processing_service, mock_processing_job
    ):
        """Test that progress is updated after each stage."""
        factory, uow = mock_uow_factory
        worker = DocumentProcessingWorker(factory, mock_processing_service)
        document_id = uuid4()

        # Setup
        mock_processing_job.current_stage = ProcessingStage.UPLOADED
        uow.processing_job_repository.list_by_document = AsyncMock(
            return_value=[mock_processing_job]
        )
        uow.processing_job_repository.update_stage = AsyncMock()
        uow.processing_job_repository.update_status = AsyncMock()
        uow.processing_job_repository.update_heartbeat = AsyncMock()
        uow.processing_job_repository.get_by_id = AsyncMock(return_value=mock_processing_job)

        # Execute
        await worker.process(document_id)

        # Assert - progress should be updated after each stage
        progress_updates = [
            call[1]["progress"]
            for call in uow.processing_job_repository.update_status.call_args_list
            if "progress" in call[1]
        ]
        assert 25 in progress_updates  # After extraction
        assert 50 in progress_updates  # After chunking
        assert 75 in progress_updates  # After embedding
        assert 95 in progress_updates  # After FAISS indexing
