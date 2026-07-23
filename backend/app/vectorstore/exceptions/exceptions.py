"""Exceptions for vector indexing operations."""


class VectorIndexException(Exception):
    """Base exception for vector index operations.

    This exception is raised when there is a general error in vector indexing
    or search operations.
    """

    pass


class VectorIndexNotFoundException(VectorIndexException):
    """Exception raised when a vector index is not found.

    This exception is raised when attempting to operate on an index
    that doesn't exist or hasn't been created.
    """

    pass


class VectorDimensionMismatchException(VectorIndexException):
    """Exception raised when vector dimensions don't match the index.

    This exception is raised when attempting to add or search with vectors
    that have a different dimension than the index.
    """

    pass


class DuplicateVectorException(VectorIndexException):
    """Exception raised when a vector ID already exists in the index.

    This exception is raised when attempting to add a vector with an ID
    that is already present in the index.
    """

    pass
