from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProcessingStatus


class ProcessingStatusResponse(BaseModel):
    """Response schema for document processing status."""

    document_id: UUID = Field(
        description="ID of the document being processed",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    status: ProcessingStatus = Field(
        description="Current processing status",
        examples=[ProcessingStatus.PROCESSING],
    )
    progress: int = Field(
        ge=0,
        le=100,
        description="Processing progress percentage (0-100)",
        examples=[45],
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if processing failed",
        examples=["Failed to extract text from PDF"],
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when processing started",
        examples=["2024-01-01T00:00:00Z"],
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when processing completed",
        examples=["2024-01-01T00:05:00Z"],
    )
    ingestion_report: dict | None = Field(
        default=None,
        description="Detailed ingestion report containing statistics on the extraction and chunking process",
        examples=[{"ocr_used": True, "chunks_created": 19}],
    )
