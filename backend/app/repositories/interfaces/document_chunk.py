"""Interface for DocumentChunk repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository(ABC):
    """Abstract interface for DocumentChunk repository operations.

    This interface defines the contract for DocumentChunk data access operations.
    Implementations can use different backends (SQLAlchemy, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, chunk: DocumentChunk) -> DocumentChunk:
        """Create a new document chunk record.

        Args:
            chunk: The DocumentChunk entity to create.

        Returns:
            The created DocumentChunk entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        pass

    @abstractmethod
    async def get_by_id(self, chunk_id: UUID) -> DocumentChunk | None:
        """Retrieve a document chunk by its unique identifier.

        Args:
            chunk_id: The UUID of the document chunk to retrieve.

        Returns:
            The DocumentChunk entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def list_by_document(
        self, document_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[DocumentChunk]:
        """Retrieve document chunks by document ID.

        Args:
            document_id: The UUID of the document.
            offset: Number of chunks to skip.
            limit: Maximum number of chunks to return.

        Returns:
            List of DocumentChunk entities ordered by chunk_index.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks for a document.

        Args:
            document_id: The UUID of the document.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        pass

    @abstractmethod
    async def get_by_vector_id(self, vector_id: str) -> DocumentChunk | None:
        """Retrieve a document chunk by its vector ID.

        Args:
            vector_id: The vector ID of the document chunk to retrieve.

        Returns:
            The DocumentChunk entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def get_by_vector_ids(self, vector_ids: list[str]) -> list[DocumentChunk]:
        """Retrieve document chunks by their vector IDs.

        Args:
            vector_ids: List of vector IDs to retrieve.

        Returns:
            List of DocumentChunk entities for the given vector IDs.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
    async def delete(self, chunk_id: UUID) -> None:
        """Delete a document chunk by its unique identifier.

        Args:
            chunk_id: The UUID of the document chunk to delete.

        Raises:
            EntityNotFoundException: If the chunk is not found.
            DatabaseOperationException: If the deletion fails.
        """
        pass
