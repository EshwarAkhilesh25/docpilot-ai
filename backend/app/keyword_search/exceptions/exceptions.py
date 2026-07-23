"""Exceptions for keyword search module."""


class KeywordIndexError(Exception):
    """Base exception for keyword index errors."""

    pass


class KeywordIndexCreationError(KeywordIndexError):
    """Exception raised when keyword index creation fails."""

    pass


class KeywordIndexSearchError(KeywordIndexError):
    """Exception raised when keyword search fails."""

    pass


class KeywordIndexPersistenceError(KeywordIndexError):
    """Exception raised when keyword index persistence operations fail."""

    pass
