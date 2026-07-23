"""Tests for BM25 provider."""

from uuid import UUID, uuid4

from app.keyword_search.providers.bm25_provider import BM25Provider


class TestBM25Provider:
    """Tests for BM25Provider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = BM25Provider()
        assert provider._index_path is None
        assert provider._corpus == []
        assert provider._chunk_ids == []
        assert provider._metadata == {}
        assert provider._chunk_id_to_index == {}
        assert provider._bm25_index is None
        assert provider._index_size == 0

    def test_initialization_with_path(self):
        """Test provider initialization with index path."""
        provider = BM25Provider(index_path="test_index")
        assert provider._index_path == "test_index"

    def test_create_index(self):
        """Test index creation."""
        provider = BM25Provider()
        provider.create_index()

        assert provider._corpus == []
        assert provider._chunk_ids == []
        assert provider._metadata == {}
        assert provider._chunk_id_to_index == {}
        assert provider._bm25_index is None
        assert provider._index_size == 0

    def test_add_chunk(self):
        """Test adding a single chunk."""
        provider = BM25Provider()
        provider.create_index()

        chunk_id = str(uuid4())
        text = "This is a test chunk"
        provider.add_chunk(chunk_id, text)

        assert provider._index_size == 1
        assert chunk_id in provider._chunk_id_to_index
        assert provider._corpus == [text]
        assert provider._chunk_ids == [chunk_id]

    def test_add_chunk_with_metadata(self):
        """Test adding a chunk with metadata."""
        provider = BM25Provider()
        provider.create_index()

        chunk_id = str(uuid4())
        text = "Test chunk"
        metadata = {"page": 1, "document": "doc1"}
        provider.add_chunk(chunk_id, text, metadata)

        assert provider._index_size == 1
        assert provider._metadata[chunk_id] == metadata

    def test_add_duplicate_chunk(self):
        """Test adding duplicate chunk (should skip)."""
        provider = BM25Provider()
        provider.create_index()

        chunk_id = str(uuid4())
        text = "Test chunk"
        provider.add_chunk(chunk_id, text)
        provider.add_chunk(chunk_id, text)  # Duplicate

        assert provider._index_size == 1

    def test_add_chunks(self):
        """Test adding multiple chunks."""
        provider = BM25Provider()
        provider.create_index()

        chunks = [(str(uuid4()), f"Chunk {i}", None) for i in range(5)]
        provider.add_chunks(chunks)

        assert provider._index_size == 5
        assert len(provider._corpus) == 5
        assert len(provider._chunk_ids) == 5

    def test_remove_chunk(self):
        """Test removing a chunk."""
        provider = BM25Provider()
        provider.create_index()

        chunk_id = str(uuid4())
        provider.add_chunk(chunk_id, "Test chunk")
        provider.remove_chunk(chunk_id)

        assert provider._index_size == 0
        assert chunk_id not in provider._chunk_id_to_index

    def test_remove_nonexistent_chunk(self):
        """Test removing a chunk that doesn't exist (should not raise)."""
        provider = BM25Provider()
        provider.create_index()

        chunk_id = str(uuid4())
        provider.remove_chunk(chunk_id)  # Should not raise

        assert provider._index_size == 0

    def test_remove_chunks(self):
        """Test removing multiple chunks."""
        provider = BM25Provider()
        provider.create_index()

        chunk_ids = [str(uuid4()) for _ in range(5)]
        for chunk_id in chunk_ids:
            provider.add_chunk(chunk_id, f"Chunk {chunk_id}")

        provider.remove_chunks(chunk_ids[:3])

        assert provider._index_size == 2

    def test_search(self):
        """Test searching the index."""
        provider = BM25Provider()
        provider.create_index()

        # Add chunks
        chunks = [
            (str(uuid4()), "invoice number 12345", None),
            (str(uuid4()), "employee ID 67890", None),
            (str(uuid4()), "API endpoint /users", None),
        ]
        provider.add_chunks(chunks)

        # Search for "invoice"
        results = provider.search("invoice", top_k=2)

        assert len(results) > 0
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        assert all(isinstance(r[0], UUID) and isinstance(r[1], float) for r in results)

    def test_search_empty_index(self):
        """Test searching an empty index."""
        provider = BM25Provider()
        provider.create_index()

        results = provider.search("test", top_k=5)

        assert results == []

    def test_save_and_load_index(self, tmp_path):
        """Test saving and loading index."""
        index_file = tmp_path / "bm25_index.pkl"

        provider = BM25Provider()
        provider.create_index()

        # Add chunks
        chunks = [(str(uuid4()), f"Chunk {i}", None) for i in range(3)]
        provider.add_chunks(chunks)

        # Save
        provider.save_index(str(index_file))
        assert index_file.exists()

        # Load into new provider
        new_provider = BM25Provider()
        new_provider.load_index(str(index_file))

        assert new_provider._index_size == 3
        assert len(new_provider._corpus) == 3

    def test_load_nonexistent_index(self, tmp_path):
        """Test loading a nonexistent index (should create new)."""
        index_file = tmp_path / "nonexistent.pkl"

        provider = BM25Provider()
        provider.load_index(str(index_file))

        # Should create new index
        assert provider._index_size == 0

    def test_rebuild_index(self):
        """Test rebuilding the index."""
        provider = BM25Provider()

        chunks = [(str(uuid4()), f"Chunk {i}", None) for i in range(5)]
        provider.rebuild_index(chunks)

        assert provider._index_size == 5
        assert len(provider._corpus) == 5

    def test_get_index_size(self):
        """Test getting index size."""
        provider = BM25Provider()
        provider.create_index()

        assert provider.get_index_size() == 0

        provider.add_chunk(str(uuid4()), "Test")
        assert provider.get_index_size() == 1

    def test_tokenization(self):
        """Test tokenization."""
        provider = BM25Provider()

        tokens = provider._tokenize("Hello World! This is a test.")

        # Should lowercase and split on word boundaries
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "!" not in tokens  # Punctuation removed
