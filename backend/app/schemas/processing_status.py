from datetime import datetime
from uuid import UUID

from app.models.enums import ProcessingStage, ProcessingStatus


class ProcessingStatusResponse:
    """Response schema for document processing status."""

    def __init__(
        self,
        document_id: UUID,
        processing_status: ProcessingStatus,
        current_stage: ProcessingStage | None,
        progress: int,
        retry_count: int,
        started_at: datetime | None,
        completed_at: datetime | None,
        last_heartbeat: datetime | None,
        error_message: str | None,
        ingestion_report: dict | None = None,
    ):
        self.document_id = document_id
        self.processing_status = processing_status
        self.current_stage = current_stage
        self.progress = progress
        self.retry_count = retry_count
        self.started_at = started_at
        self.completed_at = completed_at
        self.last_heartbeat = last_heartbeat
        self.error_message = error_message
        self.ingestion_report = ingestion_report

    def model_dump(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "document_id": self.document_id,
            "processing_status": self.processing_status,
            "current_stage": self.current_stage,
            "status": self.processing_status,
            "stage": self.current_stage,
            "progress": self.progress,
            "retry_count": self.retry_count,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "last_heartbeat": self.last_heartbeat,
            "error_message": self.error_message,
            "ingestion_report": self.ingestion_report,
        }
