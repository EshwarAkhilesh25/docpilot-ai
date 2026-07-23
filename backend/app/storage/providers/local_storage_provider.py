"""Local filesystem storage provider implementation."""

import asyncio
import re
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings
from app.storage.exceptions import (
    FileNotFoundException,
    FileStorageException,
)
from app.storage.interfaces.storage_provider import StorageProvider

settings = get_settings()


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider.

    This implementation stores files on the local filesystem under a
    configured root directory. It includes security measures to prevent
    path traversal attacks and normalizes filenames.
    """

    def __init__(self, root_directory: str | None = None) -> None:
        """Initialize the local storage provider.

        Args:
            root_directory: The root directory for file storage.
                           If None, uses STORAGE_PATH from config.
        """
        self._root = Path(root_directory or settings.STORAGE_PATH).resolve()
        self._ensure_root_directory()

    def _ensure_root_directory(self) -> None:
        """Ensure the root directory exists."""
        self._root.mkdir(parents=True, exist_ok=True)

    def _normalize_filename(self, filename: str) -> str:
        """Normalize a filename to prevent path traversal and invalid characters.

        Args:
            filename: The original filename.

        Returns:
            A normalized safe filename.
        """
        # Convert Windows separators to Unix to handle Windows paths on Linux
        filename = filename.replace("\\", "/")
        # Remove any path components (prevent path traversal)
        safe_filename = Path(filename).name

        # Remove or replace problematic characters
        # Keep alphanumeric, hyphens, underscores, dots, and spaces
        safe_filename = re.sub(r"[^\w\s\-\.]", "", safe_filename)

        # Replace multiple spaces with single space
        safe_filename = re.sub(r"\s+", " ", safe_filename).strip()

        # Ensure filename is not empty
        if not safe_filename:
            safe_filename = "unnamed_file"

        return safe_filename

    def _get_full_path(self, file_path: str) -> Path:
        """Get the full filesystem path for a storage path.

        Args:
            file_path: The relative storage path.

        Returns:
            The absolute filesystem path.

        Raises:
            FileStorageException: If the path is outside the root directory.
        """
        full_path = (self._root / file_path).resolve()

        # Prevent path traversal attacks
        if not str(full_path).startswith(str(self._root)):
            raise FileStorageException(f"Path traversal attempt detected: {file_path}")

        return full_path

    async def save(
        self,
        file_path: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Save a file to local storage.

        Args:
            file_path: The path where the file should be stored.
            content: The file content as bytes or a binary I/O stream.
            content_type: Optional MIME type (not used in local storage).

        Returns:
            The full storage path where the file was saved.

        Raises:
            FileStorageException: If the file cannot be saved.
        """
        try:
            full_path = self._get_full_path(file_path)

            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content asynchronously
            if isinstance(content, bytes):
                await asyncio.to_thread(full_path.write_bytes, content)
            else:
                # Handle BinaryIO
                def _write_stream():
                    with full_path.open("wb") as f:
                        if hasattr(content, "read"):
                            # For file-like objects, read in chunks
                            content.seek(0)
                            chunk_size = 8192
                            while chunk := content.read(chunk_size):
                                f.write(chunk)
                        else:
                            raise FileStorageException(
                                "Invalid content type: expected bytes or BinaryIO"
                            )

                await asyncio.to_thread(_write_stream)

            return file_path

        except OSError as e:
            raise FileStorageException(f"Failed to save file: {e}")

    async def delete(self, file_path: str) -> None:
        """Delete a file from local storage.

        Args:
            file_path: The path of the file to delete.

        Raises:
            FileNotFoundException: If the file does not exist.
            FileStorageException: If the file cannot be deleted.
        """
        try:
            full_path = self._get_full_path(file_path)

            if not full_path.exists():
                raise FileNotFoundException(file_path)

            await asyncio.to_thread(full_path.unlink)

        except FileNotFoundError:
            raise FileNotFoundException(file_path)
        except OSError as e:
            raise FileStorageException(f"Failed to delete file: {e}")

    async def exists(self, file_path: str) -> bool:
        """Check if a file exists in local storage.

        Args:
            file_path: The path to check.

        Returns:
            True if the file exists, False otherwise.
        """
        try:
            full_path = self._get_full_path(file_path)
            return await asyncio.to_thread(full_path.exists)
        except FileStorageException:
            return False

    async def open(self, file_path: str) -> BinaryIO:
        """Open a file for reading from local storage.

        Args:
            file_path: The path of the file to open.

        Returns:
            A binary I/O stream for reading the file.

        Raises:
            FileNotFoundException: If the file does not exist.
            FileStorageException: If the file cannot be opened.
        """
        try:
            full_path = self._get_full_path(file_path)

            if not full_path.exists():
                raise FileNotFoundException(file_path)

            def _open_file():
                return full_path.open("rb")

            return await asyncio.to_thread(_open_file)

        except FileNotFoundError:
            raise FileNotFoundException(file_path)
        except OSError as e:
            raise FileStorageException(f"Failed to open file: {e}")

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
        # Normalize user_id and document_id to prevent path traversal
        safe_user_id = re.sub(r"[^\w\-]", "", str(user_id))
        safe_document_id = re.sub(r"[^\w\-]", "", str(document_id))
        safe_filename = self._normalize_filename(filename)

        return f"{safe_user_id}/{safe_document_id}/{safe_filename}"
