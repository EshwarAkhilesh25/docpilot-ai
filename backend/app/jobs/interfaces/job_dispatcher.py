"""Interface for job dispatcher."""

from abc import ABC, abstractmethod
from uuid import UUID


class JobDispatcher(ABC):
    """Abstract interface for job dispatching.

    This interface defines the contract for dispatching background jobs.
    Implementations can use different backends (in-process, Celery, Dramatiq, RQ, etc.)
    without changing application code.
    """

    @abstractmethod
    async def enqueue_document_processing(self, document_id: UUID) -> None:
        """Enqueue a document processing job.

        Args:
            document_id: The UUID of the document to process.

        Raises:
            JobDispatchException: If the job cannot be enqueued.
        """
        pass

    @abstractmethod
    async def enqueue_document_deletion(self, document_id: UUID) -> None:
        """Enqueue a document deletion job.

        Args:
            document_id: The UUID of the document to delete.

        Raises:
            JobDispatchException: If the job cannot be enqueued.
        """
        pass
