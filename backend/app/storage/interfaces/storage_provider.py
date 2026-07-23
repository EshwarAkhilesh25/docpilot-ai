from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Abstract interface for storage providers.

    This interface defines the contract for file storage operations.
    Implementations can be for local storage, cloud storage (S3, Azure, etc.),
    or any other storage backend. The application code depends on this
    abstraction, allowing storage backends to be swapped without changes.
    """

    @abstractmethod
    async def save(
        self,
        file_path: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Save a file to storage.

        Args:
            file_path: The path where the file should be stored.
            content: The file content as bytes or a binary I/O stream.
            content_type: Optional MIME type of the content.

        Returns:
            The full storage path where the file was saved.

        Raises:
            FileStorageException: If the file cannot be saved.
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> None:
        """Delete a file from storage.

        Args:
            file_path: The path of the file to delete.

        Raises:
            FileNotFoundException: If the file does not exist.
            FileStorageException: If the file cannot be deleted.
        """
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Check if a file exists in storage.

        Args:
            file_path: The path to check.

        Returns:
            True if the file exists, False otherwise.
        """
        pass

    @abstractmethod
    async def open(self, file_path: str) -> BinaryIO:
        """Open a file for reading.

        Args:
            file_path: The path of the file to open.

        Returns:
            A binary I/O stream for reading the file.

        Raises:
            FileNotFoundException: If the file does not exist.
            FileStorageException: If the file cannot be opened.
        """
        pass

    @abstractmethod
    def generate_storage_path(
        self,
        user_id: str,
        document_id: str,
        filename: str,
    ) -> str:
        """Generate a storage path for a file.

        Args:
            user_id: The ID of the user who owns the file.
            document_id: The ID of the document.
            filename: The original filename.

        Returns:
            A storage path in the format: {user_id}/{document_id}/{filename}
        """
        pass
