from abc import ABC, abstractmethod
from uuid import UUID


class DocumentDownloadService(ABC):
    """Abstract service interface for document download operations.

    This interface defines the contract for document download business logic operations.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
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
