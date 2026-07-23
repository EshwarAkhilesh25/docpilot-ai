from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import FileType, ProcessingStage, ProcessingStatus


class DocumentResponse(BaseModel):
    """Response schema for document details."""

    id: UUID = Field(
        description="Unique identifier of the document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: UUID = Field(
        description="ID of the user who owns the document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    original_filename: str = Field(
        description="Original filename as uploaded by the user",
        examples=["report.pdf"],
    )
    stored_filename: str = Field(
        description="Generated filename used for storage",
        examples=["doc_123.pdf"],
    )
    file_type: FileType = Field(
        description="Type of the file",
        examples=[FileType.PDF],
    )
    mime_type: str = Field(
        description="MIME type of the file",
        examples=["application/pdf"],
    )
    file_size: int = Field(
        description="File size in bytes",
        examples=[1048576],
    )
    storage_path: str = Field(
        description="Path where the file is stored",
        examples=["documents/doc_123.pdf"],
    )
    processing_status: ProcessingStatus = Field(
        description="Current processing status",
        examples=[ProcessingStatus.COMPLETED],
    )
    processing_stage: ProcessingStage | None = Field(
        default=None,
        description="Current processing stage",
        examples=[ProcessingStage.COMPLETED],
    )
    summary: str | None = Field(
        default=None,
        description="AI-generated summary of the document",
        examples=["This document discusses..."],
    )
    uploaded_at: datetime = Field(
        description="Timestamp when the document was uploaded",
        examples=["2024-01-01T00:00:00Z"],
    )
    processed_at: datetime | None = Field(
        default=None,
        description="Timestamp when processing completed",
        examples=["2024-01-01T00:05:00Z"],
    )
    page_count: int | None = Field(
        default=None,
        description="Number of pages in the document",
        examples=[10],
    )
    character_count: int | None = Field(
        default=None,
        description="Number of characters in the document",
        examples=[5000],
    )
    chunk_count: int | None = Field(
        default=None,
        description="Number of chunks the document was split into",
        examples=[25],
    )


class DocumentSummaryResponse(BaseModel):
    """Response schema for document summary (lightweight)."""

    id: UUID = Field(
        description="Unique identifier of the document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    original_filename: str = Field(
        description="Original filename",
        examples=["report.pdf"],
    )
    file_type: FileType = Field(
        description="Type of the file",
        examples=[FileType.PDF],
    )
    processing_status: ProcessingStatus = Field(
        description="Current processing status",
        examples=[ProcessingStatus.COMPLETED],
    )
    uploaded_at: datetime = Field(
        description="Upload timestamp",
        examples=["2024-01-01T00:00:00Z"],
    )


class DocumentListResponse(BaseModel):
    """Response schema for document list with pagination."""

    items: list[DocumentSummaryResponse] = Field(
        description="List of document summaries",
        examples=[[]],
    )
    total: int = Field(
        description="Total number of documents",
        examples=[100],
    )
    page: int = Field(
        description="Current page number",
        examples=[1],
    )
    page_size: int = Field(
        description="Number of items per page",
        examples=[20],
    )
    total_pages: int = Field(
        description="Total number of pages",
        examples=[5],
    )


class DocumentDetailsResponse(BaseModel):
    """Response schema for detailed document information."""

    id: UUID = Field(
        description="Unique identifier of the document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    original_filename: str = Field(
        description="Original filename",
        examples=["report.pdf"],
    )
    file_type: FileType = Field(
        description="Type of the file",
        examples=[FileType.PDF],
    )
    file_size: int = Field(
        description="File size in bytes",
        examples=[1048576],
    )
    processing_status: ProcessingStatus = Field(
        description="Current processing status",
        examples=[ProcessingStatus.COMPLETED],
    )
    processing_stage: ProcessingStage | None = Field(
        default=None,
        description="Current processing stage",
        examples=[ProcessingStage.COMPLETED],
    )
    uploaded_at: datetime = Field(
        description="Upload timestamp",
        examples=["2024-01-01T00:00:00Z"],
    )
    processed_at: datetime | None = Field(
        default=None,
        description="Processing completion timestamp",
        examples=["2024-01-01T00:05:00Z"],
    )
    page_count: int | None = Field(
        default=None,
        description="Number of pages",
        examples=[10],
    )
    character_count: int | None = Field(
        default=None,
        description="Number of characters",
        examples=[5000],
    )
    chunk_count: int | None = Field(
        default=None,
        description="Number of chunks",
        examples=[25],
    )
