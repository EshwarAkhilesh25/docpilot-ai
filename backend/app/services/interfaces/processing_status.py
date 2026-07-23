from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.processing_status import ProcessingStatusResponse


class ProcessingStatusService(ABC):
    """Abstract service interface for processing status operations.

    This interface defines the contract for processing status business logic operations.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
    async def get_processing_status(
        self, document_id: UUID, user_id: UUID
    ) -> ProcessingStatusResponse:
        """Get the processing status for a document.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the status.

        Returns:
            ProcessingStatusResponse containing the processing status information.

        Raises:
            DocumentServiceException: If the document does not exist or user lacks access.
        """
