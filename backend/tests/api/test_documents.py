from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import FileType, ProcessingStatus
from app.models.user import User
from app.schemas.document import DocumentDetailsResponse, DocumentListResponse
from app.schemas.processing_status import ProcessingStatusResponse
from app.services.exceptions import DocumentServiceException

client = TestClient(app)

from app.api.dependencies import (
    get_authentication_service,
    get_job_dispatcher,
    get_keyword_index_provider,
    get_storage_provider,
    get_uow,
    get_vector_index_provider,
)
from app.api.v1.documents import get_document_service


@pytest.fixture(autouse=True)
def override_dependencies(
    mock_uow,
    mock_auth_service,
    mock_storage_provider,
    mock_document_service,
    mock_vector_provider,
    mock_document_download_service,
    mock_processing_status_service,
):
    app.dependency_overrides[get_uow] = lambda: mock_uow
    app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service
    app.dependency_overrides[get_storage_provider] = lambda: mock_storage_provider
    app.dependency_overrides[get_document_service] = lambda: mock_document_service
    app.dependency_overrides[get_vector_index_provider] = lambda: mock_vector_provider

    # Import these dynamically to avoid circular imports if any, or just mock them
    from app.api.v1.documents import get_document_download_service, get_processing_status_service

    app.dependency_overrides[get_document_download_service] = lambda: mock_document_download_service
    app.dependency_overrides[get_processing_status_service] = lambda: mock_processing_status_service

    # Also override dispatcher and keyword index just in case
    app.dependency_overrides[get_job_dispatcher] = lambda: AsyncMock()
    app.dependency_overrides[get_keyword_index_provider] = lambda: AsyncMock()

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def mock_storage_provider():
    """Fixture for mocked storage provider."""
    provider = AsyncMock()
    provider.generate_storage_path = MagicMock(return_value="user123/doc456/test.pdf")
    return provider


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_current_user():
    """Fixture for mocked current user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_auth_service():
    """Fixture for mocked authentication service."""
    auth_service = AsyncMock()
    return auth_service


@pytest.fixture
def mock_document_service():
    """Fixture for mocked document service."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_vector_provider():
    """Fixture for mocked vector provider."""
    provider = AsyncMock()
    return provider


@pytest.fixture
def mock_processing_status_service():
    """Fixture for mocked processing status service."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_document_download_service():
    """Fixture for mocked document download service."""
    service = AsyncMock()
    return service


class TestUploadDocument:
    """Tests for POST /api/v1/documents/upload endpoint."""

    def test_upload_valid_pdf(
        self, mock_storage_provider, mock_uow, mock_current_user, mock_auth_service
    ):
        """Test successful PDF upload."""
        # Setup
        document_id = uuid4()
        job_id = uuid4()

        mock_document = MagicMock()
        mock_document.id = document_id

        mock_job = MagicMock()
        mock_job.id = job_id

        mock_uow.document_repository.create = AsyncMock(return_value=mock_document)
        mock_uow.processing_job_repository.create = AsyncMock(return_value=mock_job)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                with patch("app.api.dependencies.get_uow", return_value=mock_uow):
                    # Execute
                    response = client.post(
                        "/api/v1/documents/upload",
                        files={"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")},
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    assert response.status_code == 202
                    data = response.json()
                    assert "document_id" in data
                    assert "processing_job_id" in data
                    assert data["status"] == "uploaded"
                    mock_storage_provider.save.assert_called_once()
                    mock_uow.commit.assert_called_once()

    def test_upload_valid_mp3(
        self, mock_storage_provider, mock_uow, mock_current_user, mock_auth_service
    ):
        """Test successful MP3 upload."""
        # Setup
        document_id = uuid4()
        job_id = uuid4()

        mock_document = MagicMock()
        mock_document.id = document_id

        mock_job = MagicMock()
        mock_job.id = job_id

        mock_uow.document_repository.create = AsyncMock(return_value=mock_document)
        mock_uow.processing_job_repository.create = AsyncMock(return_value=mock_job)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                with patch("app.api.dependencies.get_uow", return_value=mock_uow):
                    # Execute
                    response = client.post(
                        "/api/v1/documents/upload",
                        files={"file": ("test.mp3", BytesIO(b"test content"), "audio/mpeg")},
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    assert response.status_code == 202
                    data = response.json()
                    assert "document_id" in data
                    assert "processing_job_id" in data

    def test_upload_invalid_extension(
        self, mock_storage_provider, mock_current_user, mock_auth_service
    ):
        """Test upload with invalid file extension."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.post(
                    "/api/v1/documents/upload",
                    files={
                        "file": ("test.exe", BytesIO(b"test content"), "application/octet-stream")
                    },
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400
                assert "Unsupported file type" in response.json()["detail"]

    def test_upload_no_filename(self, mock_storage_provider, mock_current_user, mock_auth_service):
        """Test upload with no filename."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("", BytesIO(b"test content"), "application/pdf")},
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 422
                assert "Expected UploadFile" in str(response.json()["detail"])

    def test_upload_oversized_file(
        self, mock_storage_provider, mock_current_user, mock_auth_service
    ):
        """Test upload with file exceeding size limit."""
        # Create a file larger than 50 MB
        large_content = b"x" * (51 * 1024 * 1024)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.pdf", BytesIO(large_content), "application/pdf")},
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 413

    def test_upload_storage_failure(
        self, mock_storage_provider, mock_current_user, mock_auth_service
    ):
        """Test upload when storage fails."""
        # Setup
        mock_storage_provider.save.side_effect = Exception("Storage error")
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")},
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 500
                assert "Failed to save file" in response.json()["detail"]

    def test_upload_database_failure(
        self, mock_storage_provider, mock_uow, mock_current_user, mock_auth_service
    ):
        """Test upload when database operation fails."""
        # Setup
        mock_storage_provider.save = AsyncMock()
        mock_uow.commit.side_effect = Exception("Database error")
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                with patch("app.api.dependencies.get_uow", return_value=mock_uow):
                    # Execute
                    response = client.post(
                        "/api/v1/documents/upload",
                        files={"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")},
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    assert response.status_code == 500
                    assert "Failed to create document record" in response.json()["detail"]
                    # Verify cleanup was attempted
                    mock_storage_provider.delete.assert_called_once()

    def test_upload_missing_token(self, mock_storage_provider):
        """Test upload with missing authentication token."""
        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            # Execute
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")},
            )

            # Assert
            assert response.status_code == 401

    def test_upload_invalid_token(self, mock_storage_provider, mock_auth_service):
        """Test upload with invalid authentication token."""
        from app.services.exceptions import InvalidCredentialsException

        mock_auth_service.verify_token = AsyncMock(
            side_effect=InvalidCredentialsException("Invalid token")
        )

        with patch("app.api.v1.documents.get_storage_provider", return_value=mock_storage_provider):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")},
                    headers={"Authorization": "Bearer invalid_token"},
                )

                # Assert
                assert response.status_code == 401


class TestListDocuments:
    """Tests for GET /api/v1/documents endpoint."""

    def test_list_documents_success(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test successful document listing."""
        # Setup
        mock_response = DocumentListResponse(
            items=[],
            total=0,
            page=1,
            page_size=20,
            total_pages=0,
        )
        mock_document_service.list_documents = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert "total" in data
                assert "page" in data
                mock_document_service.list_documents.assert_called_once()

    def test_list_documents_with_pagination(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document listing with pagination."""
        # Setup
        mock_response = DocumentListResponse(
            items=[],
            total=50,
            page=2,
            page_size=10,
            total_pages=5,
        )
        mock_document_service.list_documents = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents?page=2&page_size=10",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 2
                assert data["page_size"] == 10
                mock_document_service.list_documents.assert_called_once_with(
                    user_id=mock_current_user.id,
                    page=2,
                    page_size=10,
                    search=None,
                    status=None,
                )

    def test_list_documents_with_search(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document listing with search."""
        # Setup
        mock_response = DocumentListResponse(
            items=[],
            total=5,
            page=1,
            page_size=20,
            total_pages=1,
        )
        mock_document_service.list_documents = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents?search=report",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                mock_document_service.list_documents.assert_called_once_with(
                    user_id=mock_current_user.id,
                    page=1,
                    page_size=20,
                    search="report",
                    status=None,
                )

    def test_list_documents_with_status_filter(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document listing with status filter."""
        # Setup
        mock_response = DocumentListResponse(
            items=[],
            total=3,
            page=1,
            page_size=20,
            total_pages=1,
        )
        mock_document_service.list_documents = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents?status=completed",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                mock_document_service.list_documents.assert_called_once_with(
                    user_id=mock_current_user.id,
                    page=1,
                    page_size=20,
                    search=None,
                    status=ProcessingStatus.COMPLETED,
                )

    def test_list_documents_invalid_page(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document listing with invalid page number."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents?page=0",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 422

    def test_list_documents_invalid_page_size(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document listing with invalid page size."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents?page_size=101",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 422


class TestGetDocument:
    """Tests for GET /api/v1/documents/{id} endpoint."""

    def test_get_document_success(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test successful document retrieval."""
        # Setup
        document_id = uuid4()
        mock_response = DocumentDetailsResponse(
            id=document_id,
            original_filename="test.pdf",
            file_type=FileType.PDF,
            file_size=1024,
            processing_status=ProcessingStatus.COMPLETED,
            uploaded_at="2024-01-01T00:00:00Z",
        )
        mock_document_service.get_document = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == str(document_id)
                mock_document_service.get_document.assert_called_once_with(
                    document_id, mock_current_user.id
                )

    def test_get_document_not_found(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document retrieval when document not found."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document = AsyncMock(
            side_effect=DocumentServiceException("Document not found")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_document_unauthorized(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document retrieval when user lacks access."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document = AsyncMock(
            side_effect=DocumentServiceException("Access denied")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_document_invalid_id(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document retrieval with invalid UUID."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents/invalid-uuid",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400


class TestDeleteDocument:
    """Tests for DELETE /api/v1/documents/{id} endpoint."""

    def test_delete_document_success(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test successful document deletion."""
        # Setup
        document_id = uuid4()
        mock_document_service.delete_document = AsyncMock()
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.delete(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 204
                mock_document_service.delete_document.assert_called_once_with(
                    document_id, mock_current_user.id
                )

    def test_delete_document_not_found(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document deletion when document not found."""
        # Setup
        document_id = uuid4()
        mock_document_service.delete_document = AsyncMock(
            side_effect=DocumentServiceException("Document not found")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.delete(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_delete_document_unauthorized(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document deletion when user lacks access."""
        # Setup
        document_id = uuid4()
        mock_document_service.delete_document = AsyncMock(
            side_effect=DocumentServiceException("Access denied")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.delete(
                    f"/api/v1/documents/{document_id}",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_delete_document_invalid_id(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test document deletion with invalid UUID."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.delete(
                    "/api/v1/documents/invalid-uuid",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400


class TestGetDocumentSummary:
    """Tests for GET /api/v1/documents/{id}/summary endpoint."""

    def test_get_document_summary_success(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test successful summary retrieval."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document_summary = AsyncMock(
            return_value={"summary": "This is a test summary"}
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/summary",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["summary"] == "This is a test summary"
                mock_document_service.get_document_summary.assert_called_once_with(
                    document_id, mock_current_user.id
                )

    def test_get_document_summary_not_available(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test summary retrieval when summary not available."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document_summary = AsyncMock(return_value=None)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/summary",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["summary"] is None

    def test_get_document_summary_not_found(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test summary retrieval when document not found."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document_summary = AsyncMock(
            side_effect=DocumentServiceException("Document not found")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/summary",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_document_summary_unauthorized(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test summary retrieval when user lacks access."""
        # Setup
        document_id = uuid4()
        mock_document_service.get_document_summary = AsyncMock(
            side_effect=DocumentServiceException("Access denied")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/summary",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_document_summary_invalid_id(
        self, mock_document_service, mock_current_user, mock_auth_service
    ):
        """Test summary retrieval with invalid UUID."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch("app.api.v1.documents.get_document_service", return_value=mock_document_service):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents/invalid-uuid/summary",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400


class TestGetProcessingStatus:
    """Tests for GET /api/v1/documents/{id}/processing-status endpoint."""

    def test_get_processing_status_success(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test successful processing status retrieval."""
        # Setup
        document_id = uuid4()
        mock_response = ProcessingStatusResponse(
            document_id=document_id,
            processing_status=ProcessingStatus.PROCESSING,
            current_stage="chunking",
            progress=50,
            retry_count=0,
            started_at="2024-01-01T00:00:00Z",
            completed_at=None,
            last_heartbeat="2024-01-01T00:05:00Z",
            error_message=None,
        )
        mock_processing_status_service.get_processing_status = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["document_id"] == str(document_id)
                assert data["processing_status"] == "processing"
                assert data["progress"] == 50
                mock_processing_status_service.get_processing_status.assert_called_once_with(
                    document_id, mock_current_user.id
                )

    def test_get_processing_status_completed(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval for completed document."""
        # Setup
        document_id = uuid4()
        mock_response = ProcessingStatusResponse(
            document_id=document_id,
            processing_status=ProcessingStatus.COMPLETED,
            current_stage="completed",
            progress=100,
            retry_count=0,
            started_at="2024-01-01T00:00:00Z",
            completed_at="2024-01-01T00:10:00Z",
            last_heartbeat="2024-01-01T00:10:00Z",
            error_message=None,
        )
        mock_processing_status_service.get_processing_status = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"
        assert data["progress"] == 100

    def test_get_processing_status_failed(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval for failed document."""
        # Setup
        document_id = uuid4()
        mock_response = ProcessingStatusResponse(
            document_id=document_id,
            processing_status=ProcessingStatus.FAILED,
            current_stage="failed",
            progress=50,
            retry_count=1,
            started_at="2024-01-01T00:00:00Z",
            completed_at="2024-01-01T00:05:00Z",
            last_heartbeat="2024-01-01T00:05:00Z",
            error_message="Processing failed: timeout",
        )
        mock_processing_status_service.get_processing_status = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "failed"
        assert data["error_message"] == "Processing failed: timeout"
        assert data["retry_count"] == 1

    def test_get_processing_status_processing(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval for actively processing document."""
        # Setup
        document_id = uuid4()
        mock_response = ProcessingStatusResponse(
            document_id=document_id,
            processing_status=ProcessingStatus.PROCESSING,
            current_stage="embedding",
            progress=75,
            retry_count=0,
            started_at="2024-01-01T00:00:00Z",
            completed_at=None,
            last_heartbeat="2024-01-01T00:07:00Z",
            error_message=None,
        )
        mock_processing_status_service.get_processing_status = AsyncMock(return_value=mock_response)
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "processing"
        assert data["current_stage"] == "embedding"
        assert data["progress"] == 75

    def test_get_processing_status_not_found(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval when document not found."""
        # Setup
        document_id = uuid4()
        mock_processing_status_service.get_processing_status = AsyncMock(
            side_effect=DocumentServiceException("Document not found")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_processing_status_unauthorized(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval when user lacks access."""
        # Setup
        document_id = uuid4()
        mock_processing_status_service.get_processing_status = AsyncMock(
            side_effect=DocumentServiceException("Access denied")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_get_processing_status_invalid_id(
        self, mock_processing_status_service, mock_current_user, mock_auth_service
    ):
        """Test processing status retrieval with invalid UUID."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_processing_status_service",
            return_value=mock_processing_status_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents/invalid-uuid/processing-status",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400


class TestDownloadDocument:
    """Tests for GET /api/v1/documents/{id}/download endpoint."""

    def test_download_document_success(
        self, mock_document_download_service, mock_current_user, mock_auth_service
    ):
        """Test successful document download."""
        # Setup

        document_id = uuid4()

        async def mock_async_generator():
            yield b"test content"

        mock_download_info = {
            "filename": "test.pdf",
            "mime_type": "application/pdf",
            "file_stream": mock_async_generator(),
        }
        mock_document_download_service.download_document = AsyncMock(
            return_value=mock_download_info
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_document_download_service",
            return_value=mock_document_download_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/download",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 200
                mock_document_download_service.download_document.assert_called_once_with(
                    document_id, mock_current_user.id
                )

    def test_download_document_not_found(
        self, mock_document_download_service, mock_current_user, mock_auth_service
    ):
        """Test download when document not found."""
        # Setup
        document_id = uuid4()
        mock_document_download_service.download_document = AsyncMock(
            side_effect=DocumentServiceException("Document not found")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_document_download_service",
            return_value=mock_document_download_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/download",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_download_document_unauthorized(
        self, mock_document_download_service, mock_current_user, mock_auth_service
    ):
        """Test download when user lacks access."""
        # Setup
        document_id = uuid4()
        mock_document_download_service.download_document = AsyncMock(
            side_effect=DocumentServiceException("Access denied")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_document_download_service",
            return_value=mock_document_download_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/download",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_download_document_missing_storage_file(
        self, mock_document_download_service, mock_current_user, mock_auth_service
    ):
        """Test download when file is missing from storage."""
        # Setup
        document_id = uuid4()
        mock_document_download_service.download_document = AsyncMock(
            side_effect=DocumentServiceException("File not found in storage")
        )
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_document_download_service",
            return_value=mock_document_download_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    f"/api/v1/documents/{document_id}/download",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 404

    def test_download_document_invalid_id(
        self, mock_document_download_service, mock_current_user, mock_auth_service
    ):
        """Test download with invalid UUID."""
        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        with patch(
            "app.api.v1.documents.get_document_download_service",
            return_value=mock_document_download_service,
        ):
            with patch(
                "app.api.dependencies.get_authentication_service", return_value=mock_auth_service
            ):
                # Execute
                response = client.get(
                    "/api/v1/documents/invalid-uuid/download",
                    headers={"Authorization": "Bearer test_token"},
                )

                # Assert
                assert response.status_code == 400
