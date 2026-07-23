from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.processing import ProcessingStatusResponse


class ProcessingService(ABC):
    """Abstract service interface for document processing operations.

    This interface defines the contract for document processing business logic.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
    async def get_processing_status(
        self, document_id: UUID, user_id: UUID
    ) -> ProcessingStatusResponse:
        """Retrieve the processing status of a document.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the status.

        Returns:
            ProcessingStatusResponse containing current processing information.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
        """

    @abstractmethod
    async def retry_processing(self, document_id: UUID, user_id: UUID) -> UUID:
        """Retry processing for a failed document.

        Args:
            document_id: The UUID of the document to reprocess.
            user_id: The UUID of the user requesting the retry.

        Returns:
            The UUID of the new processing job.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
            ValidationError: If the document is not in a retryable state.
        """

    @abstractmethod
    async def cancel_processing(self, document_id: UUID, user_id: UUID) -> None:
        """Cancel an ongoing processing job.

        Args:
            document_id: The UUID of the document whose processing to cancel.
            user_id: The UUID of the user requesting cancellation.

        Raises:
            NotFoundError: If the document does not exist or user lacks access.
            ValidationError: If the processing cannot be cancelled.
        """
