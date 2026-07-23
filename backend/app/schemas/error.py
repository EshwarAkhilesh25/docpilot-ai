from typing import Any

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    """Detail of a single validation error."""

    field: str = Field(
        description="Name of the field that failed validation",
        examples=["email"],
    )
    message: str = Field(
        description="Error message describing the validation failure",
        examples=["Invalid email format"],
    )
    type: str = Field(
        description="Type of validation error",
        examples=["value_error.email"],
    )


class ValidationErrorResponse(BaseModel):
    """Response schema for validation errors."""

    success: bool = Field(
        default=False,
        description="Always false for validation errors",
        examples=[False],
    )
    message: str = Field(
        description="General error message",
        examples=["Validation failed"],
    )
    errors: list[ValidationErrorDetail] = Field(
        description="List of validation error details",
        examples=[
            [
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "type": "value_error.email",
                }
            ]
        ],
    )


class ApiErrorResponse(BaseModel):
    """Response schema for general API errors."""

    success: bool = Field(
        default=False,
        description="Always false for error responses",
        examples=[False],
    )
    message: str = Field(
        description="Human-readable error message",
        examples=["Resource not found"],
    )
    error_code: str | None = Field(
        default=None,
        description="Machine-readable error code for programmatic handling",
        examples=["NOT_FOUND"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details",
        examples=[{"resource_id": "123"}],
    )
