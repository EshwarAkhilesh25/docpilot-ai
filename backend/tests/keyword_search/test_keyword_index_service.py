"""Tests for keyword index service."""

from unittest.mock import MagicMock
from uuid import uuid4

from app.keyword_search.services.keyword_index_service import KeywordIndexService


class TestKeywordIndexService:
    """Tests for KeywordIndexService class."""

    def test_initialization(self):
        """Test service initialization."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        assert service._keyword_index_provider is mock_provider

    def test_initialize_index_loads_existing(self, tmp_path):
        """Test initialization loads existing index."""
        mock_provider = MagicMock()
        mock_index_path = tmp_path / "bm25_index"
        mock_index_path.mkdir(parents=True, exist_ok=True)

        index_file = mock_index_path / "bm25_index.pkl"
        index_file.touch()

        service = KeywordIndexService(mock_provider)
        service._index_path = str(mock_index_path)

        # Mock load_index
        mock_provider.load_index.return_value = None

        service.initialize_index()

        mock_provider.load_index.assert_called_once()

    def test_initialize_index_creates_new(self, tmp_path):
        """Test initialization creates new index if none exists."""
        mock_provider = MagicMock()
        mock_index_path = tmp_path / "bm25_index"
        service = KeywordIndexService(mock_provider)
        service._index_path = str(mock_index_path)

        # Mock create_index
        mock_provider.create_index.return_value = None

        service.initialize_index()

        mock_provider.create_index.assert_called_once()

    def test_index_chunk(self):
        """Test indexing a single chunk."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        chunk_id = uuid4()
        text = "Test chunk"
        metadata = {"page": 1}

        service.index_chunk(chunk_id, text, metadata)

        mock_provider.add_chunk.assert_called_once_with(chunk_id, text, metadata)

    def test_index_chunks(self):
        """Test indexing multiple chunks."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        chunks = [(uuid4(), f"Chunk {i}", None) for i in range(5)]

        service.index_chunks(chunks)

        mock_provider.add_chunks.assert_called_once_with(chunks)

    def test_remove_chunk(self):
        """Test removing a chunk."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        chunk_id = uuid4()
        service.remove_chunk(chunk_id)

        mock_provider.remove_chunk.assert_called_once_with(chunk_id)

    def test_remove_chunks(self):
        """Test removing multiple chunks."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        chunk_ids = [uuid4() for _ in range(5)]
        service.remove_chunks(chunk_ids)

        mock_provider.remove_chunks.assert_called_once_with(chunk_ids)

    def test_rebuild_index(self):
        """Test rebuilding the index."""
        mock_provider = MagicMock()
        service = KeywordIndexService(mock_provider)

        chunks = [(uuid4(), f"Chunk {i}", None) for i in range(5)]
        service.rebuild_index(chunks)

        mock_provider.rebuild_index.assert_called_once_with(chunks)

    def test_save_index(self, tmp_path):
        """Test saving the index."""
        mock_provider = MagicMock()
        mock_index_path = tmp_path / "bm25_index"
        service = KeywordIndexService(mock_provider)
        service._index_path = str(mock_index_path)

        service.save_index()

        expected_path = str(mock_index_path / "bm25_index.pkl")
        mock_provider.save_index.assert_called_once_with(expected_path)

    def test_get_index_size(self):
        """Test getting index size."""
        mock_provider = MagicMock()
        mock_provider.get_index_size.return_value = 42
        service = KeywordIndexService(mock_provider)

        size = service.get_index_size()

        assert size == 42
        mock_provider.get_index_size.assert_called_once()
