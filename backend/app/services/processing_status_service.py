"""Processing status service implementation."""

import logging
import time
from collections.abc import Callable
from uuid import UUID

from app.models.enums import ProcessingStatus
from app.schemas.processing_status import ProcessingStatusResponse
from app.services.exceptions import DocumentServiceException
from app.services.interfaces.processing_status import ProcessingStatusService

logger = logging.getLogger(__name__)


class ProcessingStatusServiceImpl(ProcessingStatusService):
    """Implementation of processing status service.

    This service handles processing status retrieval with ownership validation.
    """

    def __init__(self, uow_factory: Callable):
        """Initialize the processing status service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
        """
        self._uow_factory = uow_factory

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
        time.time()
        uow = self._uow_factory()

        try:
            async with uow:
                # Verify document exists and user owns it
                document = await uow.document_repository.get_by_id(document_id)

                if document is None:
                    pass
                    raise DocumentServiceException("Document not found")

                if document.user_id != user_id:
                    pass
                    raise DocumentServiceException("Access denied")

                # Get latest processing job
                processing_job = await uow.processing_job_repository.get_latest_by_document(
                    document_id
                )

                # If no processing job exists, return current document status
                if processing_job is None:
                    response = ProcessingStatusResponse(
                        document_id=document_id,
                        processing_status=document.processing_status,
                        current_stage=None,
                        progress=(
                            100 if document.processing_status == ProcessingStatus.COMPLETED else 0
                        ),
                        retry_count=0,
                        started_at=None,
                        completed_at=document.processed_at,
                        last_heartbeat=None,
                        error_message=None,
                        ingestion_report=None,
                    )

                    pass

                    return response

                # Build response from processing job
                response = ProcessingStatusResponse(
                    document_id=document_id,
                    processing_status=processing_job.status,
                    current_stage=processing_job.current_stage,
                    progress=processing_job.progress or 0,
                    retry_count=processing_job.retry_count or 0,
                    started_at=processing_job.started_at,
                    completed_at=processing_job.completed_at,
                    last_heartbeat=processing_job.last_heartbeat,
                    error_message=processing_job.error_message,
                    ingestion_report=processing_job.ingestion_report,
                )

                pass

                return response

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to retrieve processing status: {e}")
