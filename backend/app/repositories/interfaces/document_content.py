"""Interface for DocumentContent repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.document_content import DocumentContent


class DocumentContentRepository(ABC):
    """Abstract interface for DocumentContent repository operations.

    This interface defines the contract for DocumentContent data access operations.
    Implementations can use different backends (SQLAlchemy, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, content: DocumentContent) -> DocumentContent:
        """Create a new document content record.

        Args:
            content: The DocumentContent entity to create.

        Returns:
            The created DocumentContent entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        pass

    @abstractmethod
    async def get_by_id(self, content_id: UUID) -> DocumentContent | None:
        """Retrieve a document content by its unique identifier.

        Args:
            content_id: The UUID of the document content to retrieve.

        Returns:
            The DocumentContent entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> DocumentContent | None:
        """Retrieve document content by document ID.

        Args:
            document_id: The UUID of the document.

        Returns:
            The DocumentContent entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def update(self, content: DocumentContent) -> DocumentContent:
        """Update an existing document content record.

        Args:
            content: The DocumentContent entity with updated fields.

        Returns:
            The updated DocumentContent entity.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the update fails.
        """
        pass

    @abstractmethod
    async def update_summary(self, document_id: UUID, summary: str) -> DocumentContent:
        """Update the summary field for a document content record.

        Args:
            document_id: The UUID of the document.
            summary: The summary text to set.

        Returns:
            The updated DocumentContent entity.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the update fails.
        """
        pass

    @abstractmethod
    async def delete(self, content_id: UUID) -> None:
        """Delete a document content by its unique identifier.

        Args:
            content_id: The UUID of the document content to delete.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the deletion fails.
        """
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete document content by document ID.

        Args:
            document_id: The UUID of the document.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        pass
