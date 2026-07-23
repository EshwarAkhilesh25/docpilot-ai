"""Exceptions for vector indexing."""

from app.vectorstore.exceptions.exceptions import (
    DuplicateVectorException,
    VectorDimensionMismatchException,
    VectorIndexException,
    VectorIndexNotFoundException,
)

__all__ = [
    "VectorIndexException",
    "VectorIndexNotFoundException",
    "VectorDimensionMismatchException",
    "DuplicateVectorException",
]
