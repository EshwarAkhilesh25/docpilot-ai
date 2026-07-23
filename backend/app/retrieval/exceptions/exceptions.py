"""Exceptions for retrieval operations."""


class RetrievalException(Exception):
    """Base exception for retrieval operations.

    This exception is raised when there is a general error in semantic retrieval
    operations.
    """

    pass


class IndexMetadataMismatchException(RetrievalException):
    """Exception raised when index metadata doesn't match expected configuration.

    This exception is raised when loading an index that was created with a different
    embedding model or dimension than the current configuration.
    """

    pass


class StaleVectorException(RetrievalException):
    """Exception raised when a vector ID references a deleted chunk.

    This exception is raised when attempting to retrieve a chunk whose vector ID
    exists in the index but the corresponding DocumentChunk record has been deleted.
    """

    pass
