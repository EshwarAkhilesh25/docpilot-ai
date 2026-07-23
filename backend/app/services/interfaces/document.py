from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.document import (
    DocumentDetailsResponse,
    DocumentListResponse,
)


class DocumentService(ABC):
    """Abstract service interface for document-related business operations.

    This interface defines the contract for document business logic operations.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
    async def get_document(self, document_id: UUID, user_id: UUID) -> DocumentDetailsResponse:  # type: ignore
        """Retrieve a document by its ID for a specific user.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the document.

        Returns:
            DocumentResponse containing the document details.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
        """

    @abstractmethod
    async def list_documents(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> DocumentListResponse:
        """List documents for a specific user with pagination.

        Args:
            user_id: The UUID of the user whose documents to list.
            page: The page number (1-indexed).
            page_size: The number of items per page.

        Returns:
            Paginated response containing document summaries.

        Raises:
            ValidationError: If pagination parameters are invalid.
        """

    @abstractmethod
    async def delete_document(self, document_id: UUID, user_id: UUID) -> None:
        """Delete a document for a specific user.

        Args:
            document_id: The UUID of the document to delete.
            user_id: The UUID of the user requesting deletion.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
        """

    @abstractmethod
    async def get_document_summary(self, document_id: UUID, user_id: UUID) -> dict:
        """Retrieve the AI-generated summary of a document.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the summary.

        Returns:
            A dictionary containing the document summary.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
        """
