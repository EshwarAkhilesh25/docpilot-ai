import pytest

"""Tests for ProcessingStatusService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.document import Document
from app.models.enums import ProcessingStage, ProcessingStatus
from app.models.processing_job import ProcessingJob
from app.services.exceptions import DocumentServiceException
from app.services.processing_status_service import ProcessingStatusServiceImpl


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.fixture
def mock_uow_factory(mock_uow):
    """Fixture for mocked UoW factory."""
    factory = MagicMock(return_value=mock_uow)
    return factory


@pytest.fixture
def service(mock_uow_factory):
    """Fixture for ProcessingStatusService."""
    return ProcessingStatusServiceImpl(mock_uow_factory)


@pytest.fixture
def sample_document():
    """Fixture for sample Document."""
    document_id = uuid4()
    user_id = uuid4()
    return Document(
        id=document_id,
        user_id=user_id,
        stored_filename="test.pdf",
        file_type="PDF",
        processing_status=ProcessingStatus.PROCESSING,
        storage_path="documents/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        original_filename="test.pdf",
    )


@pytest.fixture
def sample_processing_job():
    """Fixture for sample ProcessingJob."""
    job_id = uuid4()
    document_id = uuid4()
    return ProcessingJob(
        id=job_id,
        document_id=document_id,
        status=ProcessingStatus.PROCESSING,
        current_stage=ProcessingStage.CHUNKING,
        progress=50,
        retry_count=0,
        started_at=datetime.now(),
        completed_at=None,
        last_heartbeat=datetime.now(),
        error_message=None,
    )


@pytest.mark.asyncio
class TestGetProcessingStatus:
    """Tests for get_processing_status method."""

    async def test_success_with_processing_job(
        self, service, mock_uow, sample_document, sample_processing_job
    ):
        """Test successful status retrieval with active processing job."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_processing_job.document_id = sample_document.id

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_uow.processing_job_repository.get_latest_by_document.return_value = (
            sample_processing_job
        )

        # Execute
        result = await service.get_processing_status(sample_document.id, user_id)

        # Assert
        assert result.document_id == sample_document.id
        assert result.processing_status == ProcessingStatus.PROCESSING
        assert result.current_stage == ProcessingStage.CHUNKING
        assert result.progress == 50
        assert result.retry_count == 0
        assert result.started_at is not None
        assert result.completed_at is None
        assert result.last_heartbeat is not None
        assert result.error_message is None

    async def test_success_without_processing_job(self, service, mock_uow, sample_document):
        """Test successful status retrieval without processing job (uses document status)."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_document.processing_status = ProcessingStatus.COMPLETED
        sample_document.processed_at = datetime.now()

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_uow.processing_job_repository.get_latest_by_document.return_value = None

        # Execute
        result = await service.get_processing_status(sample_document.id, user_id)

        # Assert
        assert result.document_id == sample_document.id
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.current_stage is None
        assert result.progress == 100  # Completed documents show 100% progress
        assert result.retry_count == 0
        assert result.started_at is None
        assert result.completed_at is not None
        assert result.last_heartbeat is None
        assert result.error_message is None

    async def test_document_not_found(self, service, mock_uow):
        """Test status retrieval when document does not exist."""
        # Setup
        document_id = uuid4()
        user_id = uuid4()
        mock_uow.document_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(DocumentServiceException) as exc_info:
            await service.get_processing_status(document_id, user_id)

        assert "Document not found" in str(exc_info.value)

    async def test_unauthorized_access(self, service, mock_uow, sample_document):
        """Test status retrieval when user does not own the document."""
        # Setup
        user_id = uuid4()
        owner_id = uuid4()
        sample_document.user_id = owner_id

        mock_uow.document_repository.get_by_id.return_value = sample_document

        # Execute & Assert
        with pytest.raises(DocumentServiceException) as exc_info:
            await service.get_processing_status(sample_document.id, user_id)

        assert "Access denied" in str(exc_info.value)

    async def test_completed_processing(
        self, service, mock_uow, sample_document, sample_processing_job
    ):
        """Test status retrieval for completed processing."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_processing_job.document_id = sample_document.id
        sample_processing_job.status = ProcessingStatus.COMPLETED
        sample_processing_job.current_stage = ProcessingStage.COMPLETED
        sample_processing_job.progress = 100
        sample_processing_job.completed_at = datetime.now()

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_uow.processing_job_repository.get_latest_by_document.return_value = (
            sample_processing_job
        )

        # Execute
        result = await service.get_processing_status(sample_document.id, user_id)

        # Assert
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.current_stage == ProcessingStage.COMPLETED
        assert result.progress == 100
        assert result.completed_at is not None

    async def test_failed_processing(
        self, service, mock_uow, sample_document, sample_processing_job
    ):
        """Test status retrieval for failed processing."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_processing_job.document_id = sample_document.id
        sample_processing_job.status = ProcessingStatus.FAILED
        sample_processing_job.current_stage = ProcessingStage.FAILED
        sample_processing_job.progress = 50
        sample_processing_job.error_message = "Processing failed: timeout"
        sample_processing_job.completed_at = datetime.now()

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_uow.processing_job_repository.get_latest_by_document.return_value = (
            sample_processing_job
        )

        # Execute
        result = await service.get_processing_status(sample_document.id, user_id)

        # Assert
        assert result.processing_status == ProcessingStatus.FAILED
        assert result.current_stage == ProcessingStage.FAILED
        assert result.progress == 50
        assert result.error_message == "Processing failed: timeout"
        assert result.completed_at is not None

    async def test_processing_with_retry(
        self, service, mock_uow, sample_document, sample_processing_job
    ):
        """Test status retrieval for processing with retries."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_processing_job.document_id = sample_document.id
        sample_processing_job.retry_count = 2

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_uow.processing_job_repository.get_latest_by_document.return_value = (
            sample_processing_job
        )

        # Execute
        result = await service.get_processing_status(sample_document.id, user_id)

        # Assert
        assert result.retry_count == 2

    async def test_database_error(self, service, mock_uow):
        """Test status retrieval when database error occurs."""
        # Setup
        document_id = uuid4()
        user_id = uuid4()
        mock_uow.document_repository.get_by_id.side_effect = Exception("Database error")

        # Execute & Assert
        with pytest.raises(DocumentServiceException):
            await service.get_processing_status(document_id, user_id)
