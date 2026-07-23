"""Recovery service interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.processing_job import ProcessingJob


class RecoveryService(ABC):
    """Abstract interface for recovery service.

    This service is responsible for finding stale processing jobs,
    determining whether they should resume or fail, and resubmitting
    eligible jobs to the dispatcher.
    """

    @abstractmethod
    async def find_stale_jobs(self, timeout_minutes: int) -> list[ProcessingJob]:
        """Find processing jobs that have not sent a heartbeat within the timeout.

        Args:
            timeout_minutes: The timeout in minutes to consider a job stale.

        Returns:
            List of stale ProcessingJob entities.
        """

    @abstractmethod
    async def find_retryable_jobs(self, max_retries: int) -> list[ProcessingJob]:
        """Find processing jobs that can be retried (failed with retry count below max).

        Args:
            max_retries: The maximum number of retries allowed.

        Returns:
            List of retryable ProcessingJob entities.
        """

    @abstractmethod
    async def should_resume_job(self, job: ProcessingJob) -> bool:
        """Determine if a stale job should be resumed or marked as failed.

        Args:
            job: The ProcessingJob to evaluate.

        Returns:
            True if the job should be resumed, False if it should be marked as failed.
        """

    @abstractmethod
    async def resume_job(self, job_id: UUID) -> None:
        """Resume a processing job by resetting its state for reprocessing.

        Args:
            job_id: The UUID of the processing job to resume.
        """

    @abstractmethod
    async def fail_stale_job(self, job_id: UUID, reason: str) -> None:
        """Mark a stale job as failed with a reason.

        Args:
            job_id: The UUID of the processing job to fail.
            reason: The reason for marking as failed.
        """
