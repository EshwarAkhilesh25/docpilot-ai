import pytest

"""Tests for DocumentDownloadService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.document import Document
from app.models.enums import ProcessingStatus
from app.services.document_download_service import DocumentDownloadServiceImpl
from app.services.exceptions import DocumentServiceException
from app.storage.exceptions import FileStorageException


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_uow_factory(mock_uow):
    """Fixture for mocked UoW factory."""
    factory = MagicMock(return_value=mock_uow)
    return factory


@pytest.fixture
def mock_storage_provider():
    """Fixture for mocked storage provider."""
    provider = AsyncMock()
    return provider


@pytest.fixture
def service(mock_uow_factory, mock_storage_provider):
    """Fixture for DocumentDownloadService."""
    return DocumentDownloadServiceImpl(mock_uow_factory, mock_storage_provider)


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
        processing_status=ProcessingStatus.COMPLETED,
        storage_path="documents/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        original_filename="test.pdf",
    )


@pytest.fixture
def mock_file_stream():
    """Fixture for mocked file stream."""
    stream = AsyncMock()
    stream.__aiter__ = AsyncMock(return_value=iter([b"test content"]))
    return stream


@pytest.mark.asyncio
class TestDownloadDocument:
    """Tests for download_document method."""

    async def test_successful_download(
        self, service, mock_uow, mock_storage_provider, sample_document, mock_file_stream
    ):
        """Test successful document download preparation."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_storage_provider.open.return_value = mock_file_stream

        # Execute
        result = await service.download_document(sample_document.id, user_id)

        # Assert
        assert result["filename"] == "test.pdf"
        assert result["mime_type"] == "application/pdf"
        assert result["file_stream"] == mock_file_stream
        mock_uow.document_repository.get_by_id.assert_called_once_with(sample_document.id)
        mock_storage_provider.open.assert_called_once_with("documents/test.pdf")

    async def test_document_not_found(self, service, mock_uow):
        """Test download when document does not exist."""
        # Setup
        document_id = uuid4()
        user_id = uuid4()
        mock_uow.document_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(DocumentServiceException) as exc_info:
            await service.download_document(document_id, user_id)

        assert "Document not found" in str(exc_info.value)

    async def test_unauthorized_access(self, service, mock_uow, sample_document):
        """Test download when user does not own the document."""
        # Setup
        user_id = uuid4()
        owner_id = uuid4()
        sample_document.user_id = owner_id

        mock_uow.document_repository.get_by_id.return_value = sample_document

        # Execute & Assert
        with pytest.raises(DocumentServiceException) as exc_info:
            await service.download_document(sample_document.id, user_id)

        assert "Access denied" in str(exc_info.value)

    async def test_file_not_in_storage(
        self, service, mock_uow, mock_storage_provider, sample_document
    ):
        """Test download when file is missing from storage."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_storage_provider.open.side_effect = FileStorageException("File not found")

        # Execute & Assert
        with pytest.raises(DocumentServiceException) as exc_info:
            await service.download_document(sample_document.id, user_id)

        assert "File not found in storage" in str(exc_info.value)

    async def test_download_with_stored_filename_fallback(
        self, service, mock_uow, mock_storage_provider, sample_document, mock_file_stream
    ):
        """Test download when original_filename is None (uses stored_filename)."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_document.original_filename = None

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_storage_provider.open.return_value = mock_file_stream

        # Execute
        result = await service.download_document(sample_document.id, user_id)

        # Assert
        assert result["filename"] == "test.pdf"  # Falls back to stored_filename

    async def test_download_with_default_mime_type(
        self, service, mock_uow, mock_storage_provider, sample_document, mock_file_stream
    ):
        """Test download when mime_type is None (uses default)."""
        # Setup
        user_id = uuid4()
        sample_document.user_id = user_id
        sample_document.mime_type = None

        mock_uow.document_repository.get_by_id.return_value = sample_document
        mock_storage_provider.open.return_value = mock_file_stream

        # Execute
        result = await service.download_document(sample_document.id, user_id)

        # Assert
        assert result["mime_type"] == "application/octet-stream"

    async def test_database_error(self, service, mock_uow):
        """Test download when database error occurs."""
        # Setup
        document_id = uuid4()
        user_id = uuid4()
        mock_uow.document_repository.get_by_id.side_effect = Exception("Database error")

        # Execute & Assert
        with pytest.raises(DocumentServiceException):
            await service.download_document(document_id, user_id)
