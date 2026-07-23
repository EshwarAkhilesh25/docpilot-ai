from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.storage.exceptions import (
    FileNotFoundException,
    FileStorageException,
)
from app.storage.providers.local_storage_provider import LocalStorageProvider


@pytest.fixture
def temp_storage():
    """Fixture for temporary storage directory."""
    with TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def storage_provider(temp_storage):
    """Fixture for LocalStorageProvider with temporary directory."""
    return LocalStorageProvider(root_directory=temp_storage)


class TestLocalStorageProvider:
    """Tests for LocalStorageProvider."""

    def test_init_creates_root_directory(self, temp_storage):
        """Test that initialization creates the root directory."""
        root = Path(temp_storage) / "new_root"
        LocalStorageProvider(root_directory=str(root))

        assert root.exists()
        assert root.is_dir()

    def test_normalize_filename_basic(self, storage_provider):
        """Test basic filename normalization."""
        assert storage_provider._normalize_filename("test.pdf") == "test.pdf"
        assert storage_provider._normalize_filename("my file.txt") == "my file.txt"
        assert storage_provider._normalize_filename("file_name.doc") == "file_name.doc"

    def test_normalize_filename_removes_path_traversal(self, storage_provider):
        """Test that path traversal is removed from filename."""
        assert storage_provider._normalize_filename("../../../etc/passwd") == "passwd"
        assert storage_provider._normalize_filename("..\\..\\windows\\system32") == "system32"

    def test_normalize_filename_removes_special_chars(self, storage_provider):
        """Test that special characters are removed."""
        assert storage_provider._normalize_filename("file@#$%^&*().pdf") == "file.pdf"
        assert storage_provider._normalize_filename("file<>|?.txt") == "file.txt"

    def test_normalize_filename_empty_result(self, storage_provider):
        """Test that empty filename results in default name."""
        assert storage_provider._normalize_filename("@#$%^&*()") == "unnamed_file"
        assert storage_provider._normalize_filename("") == "unnamed_file"

    def test_generate_storage_path(self, storage_provider):
        """Test storage path generation."""
        path = storage_provider.generate_storage_path(
            user_id="user123", document_id="doc456", filename="test.pdf"
        )
        assert path == "user123/doc456/test.pdf"

    def test_generate_storage_path_normalizes_ids(self, storage_provider):
        """Test that user_id and document_id are normalized."""
        path = storage_provider.generate_storage_path(
            user_id="user@123", document_id="doc#456", filename="test.pdf"
        )
        assert path == "user123/doc456/test.pdf"

    @pytest.mark.asyncio
    async def test_save_bytes(self, storage_provider):
        """Test saving file with bytes content."""
        content = b"Hello, World!"
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.txt"
        )

        result = await storage_provider.save(file_path, content)

        assert result == file_path
        full_path = storage_provider._get_full_path(file_path)
        assert full_path.exists()
        assert full_path.read_bytes() == content

    @pytest.mark.asyncio
    async def test_save_binary_io(self, storage_provider):
        """Test saving file with BinaryIO content."""
        content = b"Binary content"
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.bin"
        )

        bio = BytesIO(content)
        result = await storage_provider.save(file_path, bio)

        assert result == file_path
        full_path = storage_provider._get_full_path(file_path)
        assert full_path.exists()
        assert full_path.read_bytes() == content

    @pytest.mark.asyncio
    async def test_save_creates_directories(self, storage_provider):
        """Test that save creates parent directories."""
        content = b"Test content"
        file_path = "user1/doc1/subdir/test.txt"

        await storage_provider.save(file_path, content)

        full_path = storage_provider._get_full_path(file_path)
        assert full_path.exists()
        assert full_path.parent.exists()

    @pytest.mark.asyncio
    async def test_save_invalid_content_type(self, storage_provider):
        """Test that invalid content type raises exception."""
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.txt"
        )

        with pytest.raises(FileStorageException):
            await storage_provider.save(file_path, "invalid content")

    @pytest.mark.asyncio
    async def test_delete_existing_file(self, storage_provider):
        """Test deleting an existing file."""
        content = b"Test content"
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.txt"
        )

        await storage_provider.save(file_path, content)
        await storage_provider.delete(file_path)

        full_path = storage_provider._get_full_path(file_path)
        assert not full_path.exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self, storage_provider):
        """Test deleting a non-existent file raises exception."""
        file_path = "user1/doc1/nonexistent.txt"

        with pytest.raises(FileNotFoundException):
            await storage_provider.delete(file_path)

    @pytest.mark.asyncio
    async def test_exists_true(self, storage_provider):
        """Test exists returns True for existing file."""
        content = b"Test content"
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.txt"
        )

        await storage_provider.save(file_path, content)

        assert await storage_provider.exists(file_path) is True

    @pytest.mark.asyncio
    async def test_exists_false(self, storage_provider):
        """Test exists returns False for non-existent file."""
        file_path = "user1/doc1/nonexistent.txt"

        assert await storage_provider.exists(file_path) is False

    @pytest.mark.asyncio
    async def test_open_existing_file(self, storage_provider):
        """Test opening an existing file."""
        content = b"Test content"
        file_path = storage_provider.generate_storage_path(
            user_id="user1", document_id="doc1", filename="test.txt"
        )

        await storage_provider.save(file_path, content)

        bio = await storage_provider.open(file_path)
        assert bio.read() == content
        bio.close()

    @pytest.mark.asyncio
    async def test_open_nonexistent_file(self, storage_provider):
        """Test opening a non-existent file raises exception."""
        file_path = "user1/doc1/nonexistent.txt"

        with pytest.raises(FileNotFoundException):
            await storage_provider.open(file_path)

    def test_get_full_path_prevents_traversal(self, storage_provider):
        """Test that path traversal attacks are prevented."""
        with pytest.raises(FileStorageException):
            storage_provider._get_full_path("../../../etc/passwd")

    def test_get_full_path_valid_path(self, storage_provider):
        """Test that valid paths are resolved correctly."""
        file_path = "user1/doc1/test.txt"
        full_path = storage_provider._get_full_path(file_path)

        assert str(full_path).startswith(str(storage_provider._root))
        assert full_path.name == "test.txt"
