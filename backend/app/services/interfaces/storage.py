from abc import ABC, abstractmethod
from io import BytesIO


class StorageProvider(ABC):
    """Abstract provider interface for file storage operations.

    This interface defines the contract for file storage operations across
    different storage backends (local, S3, GCS, etc.). Implementations should
    handle backend-specific details while adhering to this interface.
    """

    @abstractmethod
    async def upload_file(self, file_data: BytesIO, filename: str, content_type: str) -> str:
        """Upload a file to storage.

        Args:
            file_data: The file content as a BytesIO object.
            filename: The name to use for the stored file.
            content_type: The MIME type of the file.

        Returns:
            The storage path/key of the uploaded file.

        Raises:
            StorageError: If the upload fails.
        """

    @abstractmethod
    async def download_file(self, storage_path: str) -> BytesIO:
        """Download a file from storage.

        Args:
            storage_path: The storage path/key of the file to download.

        Returns:
            The file content as a BytesIO object.

        Raises:
            StorageError: If the download fails.
            NotFoundError: If the file does not exist.
        """

    @abstractmethod
    async def delete_file(self, storage_path: str) -> None:
        """Delete a file from storage.

        Args:
            storage_path: The storage path/key of the file to delete.

        Raises:
            StorageError: If the deletion fails.
            NotFoundError: If the file does not exist.
        """

    @abstractmethod
    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for file access.

        Args:
            storage_path: The storage path/key of the file.
            expires_in: URL expiration time in seconds.

        Returns:
            A presigned URL for accessing the file.

        Raises:
            StorageError: If URL generation fails.
            NotFoundError: If the file does not exist.
        """
