from typing import TypeVar

from pydantic import BaseModel, Field, field_validator
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class PaginationRequest(BaseModel):
    """Request schema for pagination parameters."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
        examples=[1],
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)",
        examples=[20],
    )

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get the limit for database queries."""
        return self.page_size


class PaginationResponse[DataT](GenericModel):
    """Response schema for paginated results.

    Generic type parameter DataT represents the type of items in the data list.
    """

    items: list[DataT] = Field(
        description="List of items for the current page",
        examples=[[]],
    )
    total: int = Field(
        description="Total number of items across all pages",
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

    @field_validator("total_pages")
    @classmethod
    def calculate_total_pages(cls, v: int, info) -> int:
        """Calculate total pages from total and page_size."""
        if "total" in info.data and "page_size" in info.data:
            total = info.data["total"]
            page_size = info.data["page_size"]
            return (total + page_size - 1) // page_size if page_size > 0 else 0
        return v

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1
