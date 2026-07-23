"""SQLAlchemy implementation of ProcessingJob repository."""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ProcessingStage, ProcessingStatus
from app.models.processing_job import ProcessingJob
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.processing_job import ProcessingJobRepository

logger = logging.getLogger(__name__)


class SQLAlchemyProcessingJobRepository(ProcessingJobRepository):
    """SQLAlchemy implementation of ProcessingJob repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        self._session = session

    async def create(self, job: ProcessingJob) -> ProcessingJob:
        """Create a new processing job in the database.

        Args:
            job: The ProcessingJob entity to create.

        Returns:
            The created ProcessingJob entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(job)
            await self._session.flush()
            await self._session.refresh(job)
            pass
            return job
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create", str(e))

    async def get_by_id(self, job_id: UUID) -> ProcessingJob | None:
        """Retrieve a processing job by its unique identifier.

        Args:
            job_id: The UUID of the processing job to retrieve.

        Returns:
            The ProcessingJob entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ProcessingJob).where(ProcessingJob.id == job_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_processing_job", str(e))

    async def list_by_document(
        self, document_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[ProcessingJob]:
        """List processing jobs for a specific document with pagination.

        Args:
            document_id: The UUID of the document.
            offset: The number of jobs to skip (for pagination).
            limit: The maximum number of jobs to return.

        Returns:
            A list of ProcessingJob entities for the document.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ProcessingJob)
                .where(ProcessingJob.document_id == document_id)
                .order_by(ProcessingJob.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("list_processing_jobs", str(e))

    async def update(self, job: ProcessingJob) -> ProcessingJob:
        """Update an existing processing job in the database.

        Args:
            job: The ProcessingJob entity with updated fields.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the job does not exist.
        """
        try:
            existing = await self.get_by_id(job.id)
            if existing is None:
                raise EntityNotFoundException("ProcessingJob", str(job.id))

            merged = await self._session.merge(job)
            await self._session.flush()
            await self._session.refresh(merged)
            pass
            return merged
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_processing_job", str(e))

    async def delete(self, job_id: UUID) -> None:
        """Delete a processing job by its unique identifier.

        Args:
            job_id: The UUID of the processing job to delete.

        Raises:
            DatabaseOperationException: If the deletion fails.
            EntityNotFoundException: If the job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            await self._session.delete(job)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete_processing_job", str(e))

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
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the processing job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            job.status = status
            if progress is not None:
                job.progress = progress
            if error_message is not None:
                job.error_message = error_message

            await self._session.flush()
            await self._session.refresh(job)
            pass
            return job
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_processing_job_status", str(e))

    async def update_stage(self, job_id: UUID, stage: ProcessingStage) -> ProcessingJob:
        """Update the current stage of a processing job.

        Args:
            job_id: The UUID of the processing job to update.
            stage: The new processing stage.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the processing job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            job.current_stage = stage
            await self._session.flush()
            await self._session.refresh(job)
            pass
            return job
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_processing_job_stage", str(e))

    async def mark_failed(self, job_id: UUID, error_message: str) -> ProcessingJob:
        """Mark a processing job as failed with an error message.

        Args:
            job_id: The UUID of the processing job to mark as failed.
            error_message: The error message describing the failure.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the processing job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            job.status = ProcessingStatus.FAILED
            job.current_stage = ProcessingStage.FAILED
            job.error_message = error_message
            job.completed_at = datetime.now()

            await self._session.flush()
            await self._session.refresh(job)
            pass
            return job
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("mark_processing_job_as_failed", str(e))

    async def increment_retry(self, job_id: UUID) -> ProcessingJob:
        """Increment the retry count for a processing job.

        Args:
            job_id: The UUID of the processing job to increment retry count for.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the processing job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            job.retry_count += 1
            job.status = ProcessingStatus.PROCESSING
            job.current_stage = ProcessingStage.UPLOADED  # Reset to start
            job.error_message = None
            job.started_at = datetime.now()

            await self._session.flush()
            await self._session.refresh(job)
            pass
            return job
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("increment_retry_count", str(e))

    async def update_heartbeat(self, job_id: UUID) -> ProcessingJob:
        """Update the last heartbeat timestamp for a processing job.

        Args:
            job_id: The UUID of the processing job to update heartbeat for.

        Returns:
            The updated ProcessingJob entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the processing job does not exist.
        """
        try:
            job = await self.get_by_id(job_id)
            if job is None:
                raise EntityNotFoundException("ProcessingJob", str(job_id))

            job.last_heartbeat = datetime.now()
            await self._session.flush()
            await self._session.refresh(job)
            return job
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_heartbeat", str(e))

    async def get_stale_jobs(self, timeout_minutes: int) -> list[ProcessingJob]:
        """Get processing jobs that have not sent a heartbeat within the timeout.

        Args:
            timeout_minutes: The timeout in minutes to consider a job stale.

        Returns:
            List of stale ProcessingJob entities.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
            result = await self._session.execute(
                select(ProcessingJob)
                .where(
                    ProcessingJob.status == ProcessingStatus.PROCESSING,
                    (ProcessingJob.last_heartbeat.is_(None))
                    | (ProcessingJob.last_heartbeat < timeout_threshold),
                )
                .order_by(ProcessingJob.last_heartbeat.asc().nullsfirst())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_stale_jobs", str(e))

    async def get_retryable_jobs(self, max_retries: int) -> list[ProcessingJob]:
        """Get processing jobs that can be retried (failed with retry count below max).

        Args:
            max_retries: The maximum number of retries allowed.

        Returns:
            List of retryable ProcessingJob entities.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            result = await self._session.execute(
                select(ProcessingJob)
                .where(
                    ProcessingJob.status == ProcessingStatus.FAILED,
                    ProcessingJob.retry_count < max_retries,
                )
                .order_by(ProcessingJob.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_retryable_jobs", str(e))

    async def get_by_document_id(self, document_id: UUID) -> ProcessingJob | None:
        """Get a processing job by document ID (returns the first one found).

        Args:
            document_id: The UUID of the document.

        Returns:
            The ProcessingJob entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            result = await self._session.execute(
                select(ProcessingJob)
                .where(ProcessingJob.document_id == document_id)
                .order_by(ProcessingJob.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "get_by_document_id", f"Failed to get processing job: {e}"
            )

    async def get_latest_by_document(self, document_id: UUID) -> ProcessingJob | None:
        """Get the latest processing job for a specific document.

        Args:
            document_id: The UUID of the document.

        Returns:
            The latest ProcessingJob entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            result = await self._session.execute(
                select(ProcessingJob)
                .where(ProcessingJob.document_id == document_id)
                .order_by(ProcessingJob.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "get_latest_by_document", f"Failed to get latest processing job: {e}"
            )
