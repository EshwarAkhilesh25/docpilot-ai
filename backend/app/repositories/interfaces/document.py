from abc import ABC, abstractmethod
from uuid import UUID

from app.models.document import Document
from app.models.enums import ProcessingStatus


class DocumentRepository(ABC):
    """Abstract repository interface for Document entity operations.

    This interface defines the contract for document data access operations.
    Implementations should handle database-specific details while adhering
    to this interface for consistency and testability.
    """

    @abstractmethod
    async def create(self, document: Document) -> Document:
        """Create a new document in the database.

        Args:
            document: The Document entity to create.

        Returns:
            The created Document entity with generated fields populated.

        Raises:
            DatabaseError: If the creation fails due to database issues.
        """

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None:
        """Retrieve a document by its unique identifier.

        Args:
            document_id: The UUID of the document to retrieve.

        Returns:
            The Document entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def list_by_user(self, user_id: UUID, offset: int = 0, limit: int = 20) -> list[Document]:
        """List documents belonging to a specific user with pagination.

        Args:
            user_id: The UUID of the user whose documents to list.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of Document entities belonging to the user.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Update an existing document in the database.

        Args:
            document: The Document entity with updated fields.

        Returns:
            The updated Document entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            NotFoundError: If the document does not exist.
        """

    @abstractmethod
    async def delete(self, document_id: UUID) -> None:
        """Delete a document by its unique identifier.

        Args:
            document_id: The UUID of the document to delete.

        Raises:
            DatabaseError: If the deletion fails due to database issues.
            NotFoundError: If the document does not exist.
        """

    @abstractmethod
    async def exists(self, document_id: UUID) -> bool:
        """Check if a document exists.

        Args:
            document_id: The UUID of the document to check.

        Returns:
            True if the document exists, False otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int:
        """Count documents belonging to a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The number of documents belonging to the user.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def search_by_filename(
        self, user_id: UUID, search_term: str, offset: int = 0, limit: int = 20
    ) -> list[Document]:
        """Search documents by filename for a specific user.

        Args:
            user_id: The UUID of the user.
            search_term: The search term to match in filenames.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of matching Document entities.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def list_by_status(
        self, user_id: UUID, status: ProcessingStatus, offset: int = 0, limit: int = 20
    ) -> list[Document]:
        """List documents by processing status for a specific user.

        Args:
            user_id: The UUID of the user.
            status: The processing status to filter by.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of Document entities with the specified status.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def get_storage_path(self, document_id: UUID) -> str | None:
        """Get the storage path for a document.

        Args:
            document_id: The UUID of the document.

        Returns:
            The storage path if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """
