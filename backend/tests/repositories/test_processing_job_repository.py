import pytest

"""Tests for ProcessingJob repository."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ProcessingStage, ProcessingStatus
from app.models.processing_job import ProcessingJob
from app.repositories.exceptions import DatabaseOperationException
from app.repositories.sqlalchemy.processing_job_repository import SQLAlchemyProcessingJobRepository


@pytest.fixture
def mock_session():
    """Fixture for mocked AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def repository(mock_session):
    """Fixture for ProcessingJobRepository."""
    return SQLAlchemyProcessingJobRepository(mock_session)


@pytest.fixture
def sample_job():
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
class TestGetByDocumentId:
    """Tests for get_by_document_id method."""

    async def test_get_by_document_id_success(self, repository, mock_session, sample_job):
        """Test successful retrieval by document ID."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_document_id(sample_job.document_id)

        # Assert
        assert result == sample_job
        mock_session.execute.assert_called_once()

    async def test_get_by_document_id_not_found(self, repository, mock_session):
        """Test retrieval when no job exists for document."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_document_id(uuid4())

        # Assert
        assert result is None

    async def test_get_by_document_id_database_error(self, repository, mock_session):
        """Test retrieval when database error occurs."""
        # Setup
        from sqlalchemy.exc import SQLAlchemyError

        mock_session.execute.side_effect = SQLAlchemyError("Database error")

        # Execute & Assert
        with pytest.raises(DatabaseOperationException):
            await repository.get_by_document_id(uuid4())


@pytest.mark.asyncio
class TestGetLatestByDocument:
    """Tests for get_latest_by_document method."""

    async def test_get_latest_by_document_success(self, repository, mock_session, sample_job):
        """Test successful retrieval of latest job by document ID."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_latest_by_document(sample_job.document_id)

        # Assert
        assert result == sample_job
        mock_session.execute.assert_called_once()

    async def test_get_latest_by_document_not_found(self, repository, mock_session):
        """Test retrieval when no job exists for document."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_latest_by_document(uuid4())

        # Assert
        assert result is None

    async def test_get_latest_by_document_database_error(self, repository, mock_session):
        """Test retrieval when database error occurs."""
        # Setup
        from sqlalchemy.exc import SQLAlchemyError

        mock_session.execute.side_effect = SQLAlchemyError("Database error")

        # Execute & Assert
        with pytest.raises(DatabaseOperationException):
            await repository.get_latest_by_document(uuid4())

    async def test_get_latest_by_document_ordering(self, repository, mock_session):
        """Test that latest job is returned when multiple jobs exist."""
        # Setup
        document_id = uuid4()
        ProcessingJob(
            id=uuid4(),
            document_id=document_id,
            status=ProcessingStatus.COMPLETED,
            current_stage=ProcessingStage.COMPLETED,
            progress=100,
            retry_count=0,
            started_at=datetime.now() - timedelta(hours=2),
            completed_at=datetime.now() - timedelta(hours=1),
            last_heartbeat=datetime.now() - timedelta(hours=1),
            error_message=None,
        )

        new_job = ProcessingJob(
            id=uuid4(),
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

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = new_job
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_latest_by_document(document_id)

        # Assert
        assert result == new_job
        assert result.status == ProcessingStatus.PROCESSING
