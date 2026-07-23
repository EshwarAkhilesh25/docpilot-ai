from datetime import datetime

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response schema for all API responses.

    Provides a consistent structure for API responses with success status,
    message, and timestamp.
    """

    success: bool = Field(
        description="Indicates whether the request was successful", examples=[True]
    )
    message: str = Field(
        description="Human-readable message describing the result",
        examples=["Operation completed successfully"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO 8601 timestamp of the response",
        examples=["2024-01-01T00:00:00Z"],
    )
