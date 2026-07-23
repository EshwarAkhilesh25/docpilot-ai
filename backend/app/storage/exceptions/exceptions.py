"""Exceptions for storage operations."""


class StorageException(Exception):
    """Base exception for storage errors."""

    pass


class FileStorageException(StorageException):
    """Raised when file storage operations fail."""

    def __init__(self, message: str):
        super().__init__(f"File storage error: {message}")


class FileNotFoundException(StorageException):
    """Raised when a requested file is not found in storage."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"File not found: {file_path}")
