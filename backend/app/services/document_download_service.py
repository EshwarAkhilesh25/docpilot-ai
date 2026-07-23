"""Document download service implementation."""

import logging
import time
from collections.abc import Callable
from uuid import UUID

from app.services.exceptions import DocumentServiceException
from app.services.interfaces.document_download import DocumentDownloadService
from app.storage.exceptions import FileStorageException
from app.storage.interfaces.storage_provider import StorageProvider

logger = logging.getLogger(__name__)


class DocumentDownloadServiceImpl(DocumentDownloadService):
    """Implementation of document download service.

    This service handles document download with ownership validation and file access.
    """

    def __init__(self, uow_factory: Callable, storage_provider: StorageProvider):
        """Initialize the document download service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            storage_provider: Storage provider for file operations.
        """
        self._uow_factory = uow_factory
        self._storage_provider = storage_provider

    async def download_document(self, document_id: UUID, user_id: UUID) -> dict:
        """Get document download information.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the download.

        Returns:
            Dictionary containing filename, mime_type, and file_stream.

        Raises:
            DocumentServiceException: If the document does not exist, user lacks access, or file is missing.
        """
        time.time()
        uow = self._uow_factory()

        try:
            async with uow:
                # Verify document exists and user owns it
                document = await uow.document_repository.get_by_id(document_id)

                if document is None:
                    pass
                    raise DocumentServiceException("Document not found")

                if document.user_id != user_id:
                    pass
                    raise DocumentServiceException("Access denied")

                # Get storage path
                storage_path = document.storage_path

                # Verify file exists in storage
                try:
                    file_stream = await self._storage_provider.open(storage_path)
                except FileStorageException:
                    pass
                    raise DocumentServiceException("File not found in storage")

                result = {
                    "filename": document.original_filename or document.stored_filename,
                    "mime_type": document.mime_type or "application/octet-stream",
                    "file_stream": file_stream,
                }

                pass

                return result

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to prepare document download: {e}")
