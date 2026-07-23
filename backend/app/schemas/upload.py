from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProcessingStatus


class UploadDocumentResponse(BaseModel):
    """Response schema for document upload."""

    document_id: UUID = Field(
        description="Unique identifier of the uploaded document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    processing_job_id: UUID = Field(
        description="Unique identifier of the processing job",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )
    status: ProcessingStatus = Field(
        description="Current processing status of the document",
        examples=[ProcessingStatus.UPLOADED],
    )
