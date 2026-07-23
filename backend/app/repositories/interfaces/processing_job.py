from abc import ABC, abstractmethod
from uuid import UUID

from app.models.enums import ProcessingStage, ProcessingStatus
from app.models.processing_job import ProcessingJob


class ProcessingJobRepository(ABC):
    """Abstract repository interface for ProcessingJob entity operations.

    This interface defines the contract for processing job data access operations.
    Implementations should handle database-specific details while adhering
    to this interface for consistency and testability.
    """

    @abstractmethod
    async def create(self, job: ProcessingJob) -> ProcessingJob:
        """Create a new processing job in the database.

        Args:
            job: The ProcessingJob entity to create.

        Returns:
            The created ProcessingJob entity with generated fields populated.

        Raises:
            DatabaseError: If the creation fails due to database issues.
        """

    @abstractmethod
    async def update_status(
        self,
        job_id: UUID,
        status: ProcessingStatus,
        progress: int | None = None,
        error_message: str | None = None,
    ) -> ProcessingJob:
        """Update the status of a processing job.

        Args:
            job_id: The UUID of the processing job to update.
            status: The new processing status.
            progress: Optional progress percentage (0-100).
            error_message: Optional error message if the job failed.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            NotFoundError: If the processing job does not exist.
        """

    @abstractmethod
    async def update_stage(self, job_id: UUID, stage: ProcessingStage) -> ProcessingJob:
        """Update the current stage of a processing job.

        Args:
            job_id: The UUID of the processing job to update.
            stage: The new processing stage.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            EntityNotFoundException: If the processing job does not exist.
        """

    @abstractmethod
    async def mark_failed(self, job_id: UUID, error_message: str) -> ProcessingJob:
        """Mark a processing job as failed with an error message.

        Args:
            job_id: The UUID of the processing job to mark as failed.
            error_message: The error message describing the failure.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            EntityNotFoundException: If the processing job does not exist.
        """

    @abstractmethod
    async def increment_retry(self, job_id: UUID) -> ProcessingJob:
        """Increment the retry count for a processing job.

        Args:
            job_id: The UUID of the processing job to increment retry count for.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            EntityNotFoundException: If the processing job does not exist.
        """

    @abstractmethod
    async def update_heartbeat(self, job_id: UUID) -> ProcessingJob:
        """Update the last heartbeat timestamp for a processing job.

        Args:
            job_id: The UUID of the processing job to update heartbeat for.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            EntityNotFoundException: If the processing job does not exist.
        """

    @abstractmethod
    async def get_stale_jobs(self, timeout_minutes: int) -> list[ProcessingJob]:
        """Get processing jobs that have not sent a heartbeat within the timeout.

        Args:
            timeout_minutes: The timeout in minutes to consider a job stale.

        Returns:
            List of stale ProcessingJob entities.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def get_retryable_jobs(self, max_retries: int) -> list[ProcessingJob]:
        """Get processing jobs that can be retried (failed with retry count below max).

        Args:
            max_retries: The maximum number of retries allowed.

        Returns:
            List of retryable ProcessingJob entities.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def list_by_document(self, document_id: UUID) -> list[ProcessingJob]:
        """List all processing jobs for a specific document.

        Args:
            document_id: The UUID of the document whose jobs to list.

        Returns:
            A list of ProcessingJob entities for the document, ordered by creation time.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> ProcessingJob | None:
        """Get a processing job by document ID (returns the first one found).

        Args:
            document_id: The UUID of the document.

        Returns:
            The ProcessingJob entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def get_latest_by_document(self, document_id: UUID) -> ProcessingJob | None:
        """Get the latest processing job for a specific document.

        Args:
            document_id: The UUID of the document.

        Returns:
            The latest ProcessingJob entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """
