"""Recovery service implementation."""

import logging
from collections.abc import Callable
from uuid import UUID

from app.models.enums import ProcessingStage
from app.models.processing_job import ProcessingJob
from app.services.exceptions import DocumentProcessingException
from app.services.interfaces.recovery import RecoveryService

logger = logging.getLogger(__name__)


class RecoveryServiceImpl(RecoveryService):
    """Implementation of recovery service.

    This service is responsible for:
    - Finding stale processing jobs
    - Determining whether they should resume or fail
    - Resubmitting eligible jobs to the dispatcher

    This service does NOT automatically execute recovery.
    It provides methods for external schedulers to call.
    """

    def __init__(
        self, uow_factory: Callable, max_stale_timeout_minutes: int = 30, max_retries: int = 3
    ):
        """Initialize the recovery service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            max_stale_timeout_minutes: Maximum timeout before considering a job stale.
            max_retries: Maximum number of retries allowed for failed jobs.
        """
        self._uow_factory = uow_factory
        self._max_stale_timeout_minutes = max_stale_timeout_minutes
        self._max_retries = max_retries

    async def find_stale_jobs(self, timeout_minutes: int) -> list[ProcessingJob]:
        """Find processing jobs that have not sent a heartbeat within the timeout.

        Args:
            timeout_minutes: The timeout in minutes to consider a job stale.

        Returns:
            List of stale ProcessingJob entities.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                stale_jobs = await uow.processing_job_repository.get_stale_jobs(timeout_minutes)
                pass
                return stale_jobs
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Failed to find stale jobs: {e}")

    async def find_retryable_jobs(self, max_retries: int) -> list[ProcessingJob]:
        """Find processing jobs that can be retried (failed with retry count below max).

        Args:
            max_retries: The maximum number of retries allowed.

        Returns:
            List of retryable ProcessingJob entities.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                retryable_jobs = await uow.processing_job_repository.get_retryable_jobs(max_retries)
                pass
                return retryable_jobs
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Failed to find retryable jobs: {e}")

    async def should_resume_job(self, job: ProcessingJob) -> bool:
        """Determine if a stale job should be resumed or marked as failed.

        A job should be resumed if:
        - It has not exceeded max retries
        - It is in a recoverable stage (not COMPLETED or already FAILED with max retries)

        Args:
            job: The ProcessingJob to evaluate.

        Returns:
            True if the job should be resumed, False if it should be marked as failed.
        """
        # Check retry count
        if job.retry_count >= self._max_retries:
            pass
            return False

        # Check current stage - jobs in COMPLETED or FAILED stages should not resume
        if job.current_stage in [ProcessingStage.COMPLETED, ProcessingStage.FAILED]:
            pass
            return False

        # Job is eligible for resume
        pass
        return True

    async def resume_job(self, job_id: UUID) -> None:
        """Resume a processing job by resetting its state for reprocessing.

        This does NOT restart the job from the beginning.
        It resets the status to PROCESSING and clears error state,
        allowing the worker to resume from the current_stage.

        Args:
            job_id: The UUID of the processing job to resume.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                job = await uow.processing_job_repository.get_by_id(job_id)
                if job is None:
                    raise DocumentProcessingException(f"Job not found: {job_id}")

                # Reset state for resume
                job.status = None  # Will be set to PROCESSING by worker
                job.error_message = None
                # Keep current_stage - worker will resume from there
                # Keep retry_count - already incremented

                await uow.processing_job_repository.update(job)
                await uow.commit()

                pass
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Failed to resume job: {e}")

    async def fail_stale_job(self, job_id: UUID, reason: str) -> None:
        """Mark a stale job as failed with a reason.

        Args:
            job_id: The UUID of the processing job to fail.
            reason: The reason for marking as failed.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                await uow.processing_job_repository.mark_failed(job_id, reason)
                await uow.commit()

                pass
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Failed to mark stale job as failed: {e}")

    async def recover_stale_jobs(self) -> dict[str, int]:
        """Recover all stale jobs.

        This method:
        1. Finds all stale jobs
        2. Determines if each should resume or fail
        3. Takes appropriate action

        Returns:
            Dictionary with recovery statistics:
            - total: Total stale jobs found
            - resumed: Jobs resumed
            - failed: Jobs marked as failed
        """
        stats = {"total": 0, "resumed": 0, "failed": 0}

        try:
            # Find stale jobs
            stale_jobs = await self.find_stale_jobs(self._max_stale_timeout_minutes)
            stats["total"] = len(stale_jobs)

            # Process each stale job
            for job in stale_jobs:
                if await self.should_resume_job(job):
                    await self.resume_job(job.id)
                    stats["resumed"] += 1
                else:
                    await self.fail_stale_job(
                        job.id, "Job exceeded max retries or in terminal state"
                    )
                    stats["failed"] += 1

            pass

            return stats
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Failed to recover stale jobs: {e}")
