"""Tests for InProcessJobDispatcher."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.jobs.dispatchers.in_process_dispatcher import InProcessJobDispatcher
from app.jobs.exceptions import JobDispatchException


@pytest.fixture
def mock_ingestion_pipeline():
    """Fixture for mocked IngestionPipeline."""
    return MagicMock()


@pytest.fixture
def mock_embedding_provider():
    """Fixture for mocked EmbeddingProvider."""
    return MagicMock()


@pytest.fixture
def dispatcher(mock_ingestion_pipeline, mock_embedding_provider):
    """Fixture for InProcessJobDispatcher."""
    return InProcessJobDispatcher(
        ingestion_pipeline=mock_ingestion_pipeline, embedding_provider=mock_embedding_provider
    )


class TestInProcessJobDispatcher:
    """Tests for InProcessJobDispatcher."""

    def test_init(self, dispatcher, mock_ingestion_pipeline, mock_embedding_provider):
        """Test dispatcher initialization."""
        assert dispatcher._worker is not None

    @pytest.mark.asyncio
    async def test_enqueue_document_processing(self, dispatcher):
        """Test enqueuing a document processing job."""
        document_id = uuid4()

        # Execute
        await dispatcher.enqueue_document_processing(document_id)

    @pytest.mark.asyncio
    async def test_enqueue_document_processing_does_not_block(self, dispatcher):
        """Test that enqueue_document_processing does not block."""
        document_id = uuid4()

        import time

        start = time.time()
        await dispatcher.enqueue_document_processing(document_id)
        elapsed = time.time() - start

        # Assert - should return immediately
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_enqueue_document_processing_failure(self, dispatcher):
        """Test enqueuing failure raises JobDispatchException."""
        document_id = uuid4()

        # Make asyncio.create_task fail
        with patch(
            "app.jobs.dispatchers.in_process_dispatcher.asyncio.create_task",
            side_effect=Exception("Task creation failed"),
        ):
            # Execute
            with pytest.raises(JobDispatchException) as exc_info:
                await dispatcher.enqueue_document_processing(document_id)

            # Assert
            assert "Failed to enqueue job" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_enqueue_document_deletion(self, dispatcher):
        """Test enqueuing a document deletion job."""
        document_id = uuid4()

        # Execute - should not raise
        await dispatcher.enqueue_document_deletion(document_id)
