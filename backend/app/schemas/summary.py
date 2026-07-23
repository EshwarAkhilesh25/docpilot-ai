from uuid import UUID

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """Response schema for document summary."""

    document_id: UUID = Field(
        description="ID of the document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    summary: str = Field(
        description="AI-generated summary of the document content",
        examples=["This document provides an overview of..."],
    )
    key_points: list[str] = Field(
        description="List of key points extracted from the document",
        examples=[["Point 1", "Point 2", "Point 3"]],
    )
