"""Tests for hybrid retrieval functionality."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.core.config import get_settings
from app.retrieval.services.retriever_service import RetrieverService


class TestHybridRetrieval:
    """Tests for hybrid retrieval in RetrieverService."""

    @pytest.fixture
    def mock_uow_factory(self):
        """Mock UnitOfWork factory."""
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.document_chunk_repository.get_by_ids = AsyncMock(return_value=[])
        uow.document_chunk_repository.get_by_id = AsyncMock(return_value=None)

        async def factory():
            return uow

        return factory

    @pytest.fixture
    def mock_embedding_provider(self):
        """Mock embedding provider."""
        provider = MagicMock()
        provider.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return provider

    @pytest.fixture
    def mock_vector_provider(self):
        """Mock vector index provider."""
        provider = MagicMock()
        return provider

    @pytest.fixture
    def mock_keyword_provider(self):
        """Mock keyword index provider."""
        provider = MagicMock()
        provider.search = MagicMock(return_value=[])
        return provider

    @pytest.fixture
    def retriever_service(
        self, mock_uow_factory, mock_embedding_provider, mock_vector_provider, mock_keyword_provider
    ):
        """Create retriever service with all dependencies."""
        return RetrieverService(
            uow_factory=mock_uow_factory,
            embedding_provider=mock_embedding_provider,
            vector_provider=mock_vector_provider,
            keyword_index_provider=mock_keyword_provider,
        )

    @pytest.mark.asyncio
    async def test_semantic_only_retrieval(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test retrieval with only semantic search (keyword disabled)."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", False):
            # Setup
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.9),
                    MagicMock(vector_id="chunk2", similarity_score=0.8),
                ]
            )

            # Mock chunk loading
            mock_chunk1 = MagicMock()
            mock_chunk1.id = uuid4()
            mock_chunk1.document_id = uuid4()
            mock_chunk1.chunk_index = 0
            mock_chunk1.text = "Test chunk 1"
            mock_chunk1.page_number = 1
            mock_chunk1.metadata = {}

            mock_chunk2 = MagicMock()
            mock_chunk2.id = uuid4()
            mock_chunk2.document_id = uuid4()
            mock_chunk2.chunk_index = 1
            mock_chunk2.text = "Test chunk 2"
            mock_chunk2.page_number = 1
            mock_chunk2.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk1,
                    "chunk2": mock_chunk2,
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=2)

            # Verify
            assert len(results) == 2
            mock_keyword_provider.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_keyword_only_retrieval(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test retrieval with only keyword search (semantic returns empty)."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(return_value=[])
            mock_keyword_provider.search = MagicMock(
                return_value=[
                    ("chunk1", 0.9),
                    ("chunk2", 0.8),
                ]
            )

            # Mock chunk loading
            mock_chunk1 = MagicMock()
            mock_chunk1.id = uuid4()
            mock_chunk1.document_id = uuid4()
            mock_chunk1.chunk_index = 0
            mock_chunk1.text = "Test chunk 1"
            mock_chunk1.page_number = 1
            mock_chunk1.metadata = {}

            mock_chunk2 = MagicMock()
            mock_chunk2.id = uuid4()
            mock_chunk2.document_id = uuid4()
            mock_chunk2.chunk_index = 1
            mock_chunk2.text = "Test chunk 2"
            mock_chunk2.page_number = 1
            mock_chunk2.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk1,
                    "chunk2": mock_chunk2,
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=2)

            # Verify
            assert len(results) == 2
            mock_keyword_provider.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_retrieval_merge(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test hybrid retrieval with merged results."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.9),
                    MagicMock(vector_id="chunk2", similarity_score=0.7),
                ]
            )
            mock_keyword_provider.search = MagicMock(
                return_value=[
                    ("chunk2", 0.8),
                    ("chunk3", 0.85),
                ]
            )

            # Mock chunk loading
            mock_chunk1 = MagicMock()
            mock_chunk1.id = uuid4()
            mock_chunk1.document_id = uuid4()
            mock_chunk1.chunk_index = 0
            mock_chunk1.text = "Test chunk 1"
            mock_chunk1.page_number = 1
            mock_chunk1.metadata = {}

            mock_chunk2 = MagicMock()
            mock_chunk2.id = uuid4()
            mock_chunk2.document_id = uuid4()
            mock_chunk2.chunk_index = 1
            mock_chunk2.text = "Test chunk 2"
            mock_chunk2.page_number = 1
            mock_chunk2.metadata = {}

            mock_chunk3 = MagicMock()
            mock_chunk3.id = uuid4()
            mock_chunk3.document_id = uuid4()
            mock_chunk3.chunk_index = 2
            mock_chunk3.text = "Test chunk 3"
            mock_chunk3.page_number = 1
            mock_chunk3.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk1,
                    "chunk2": mock_chunk2,
                    "chunk3": mock_chunk3,
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=3)

            # Verify - should have 3 unique chunks
            assert len(results) == 3
            # chunk2 should have higher score from keyword (0.8 vs 0.7)
            chunk2_result = next((r for r in results if r.chunk_id == mock_chunk2.id), None)
            assert chunk2_result is not None

    @pytest.mark.asyncio
    async def test_duplicate_merging_preserves_highest_score(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test that duplicate chunks preserve the highest score."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup - same chunk in both results with different scores
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.7),
                ]
            )
            mock_keyword_provider.search = MagicMock(
                return_value=[
                    ("chunk1", 0.9),
                ]
            )

            # Mock chunk loading
            mock_chunk = MagicMock()
            mock_chunk.id = uuid4()
            mock_chunk.document_id = uuid4()
            mock_chunk.chunk_index = 0
            mock_chunk.text = "Test chunk"
            mock_chunk.page_number = 1
            mock_chunk.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk,
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=1)

            # Verify - should preserve higher score (0.9 from keyword)
            assert len(results) == 1
            assert results[0].similarity_score == 1.0

    @pytest.mark.asyncio
    async def test_empty_indexes(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test retrieval when both indexes are empty."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(return_value=[])
            mock_keyword_provider.search = MagicMock(return_value=[])

            # Execute
            results = await retriever_service.retrieve("test query", top_k=5)

            # Verify
            assert results == []

    @pytest.mark.asyncio
    async def test_deleted_chunks_filtered(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test that deleted chunks are filtered out."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.9),
                    MagicMock(vector_id="chunk2", similarity_score=0.8),
                ]
            )

            # Mock chunk loading - chunk2 is deleted (None)
            mock_chunk = MagicMock()
            mock_chunk.id = uuid4()
            mock_chunk.document_id = uuid4()
            mock_chunk.chunk_index = 0
            mock_chunk.text = "Test chunk"
            mock_chunk.page_number = 1
            mock_chunk.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk,
                    "chunk2": None,  # Deleted
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=5)

            # Verify - only chunk1 should be returned
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_deterministic_ordering(
        self, retriever_service, mock_vector_provider, mock_keyword_provider
    ):
        """Test that results are deterministically ordered by score."""
        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.7),
                    MagicMock(vector_id="chunk2", similarity_score=0.9),
                    MagicMock(vector_id="chunk3", similarity_score=0.8),
                ]
            )
            mock_keyword_provider.search = MagicMock(return_value=[])

            # Mock chunk loading
            chunks = {}
            for i, chunk_id in enumerate(["chunk1", "chunk2", "chunk3"]):
                mock_chunk = MagicMock()
                mock_chunk.id = uuid4()
                mock_chunk.document_id = uuid4()
                mock_chunk.chunk_index = i
                mock_chunk.text = f"Chunk {i}"
                mock_chunk.page_number = 1
                mock_chunk.metadata = {}
                chunks[chunk_id] = mock_chunk

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(return_value=chunks)

            # Execute
            results = await retriever_service.retrieve("test query", top_k=3)

            # Verify - should be ordered by score (descending)
            assert len(results) == 3
            scores = [r.similarity_score for r in results]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_keyword_provider_none(self, retriever_service, mock_vector_provider):
        """Test retrieval when keyword provider is None."""
        retriever_service._keyword_index_provider = None

        with patch.object(get_settings(), "HYBRID_RETRIEVAL_ENABLED", True):
            # Setup
            mock_vector_provider.search = AsyncMock(
                return_value=[
                    MagicMock(vector_id="chunk1", similarity_score=0.9),
                ]
            )

            # Mock chunk loading
            mock_chunk = MagicMock()
            mock_chunk.id = uuid4()
            mock_chunk.document_id = uuid4()
            mock_chunk.chunk_index = 0
            mock_chunk.text = "Test chunk"
            mock_chunk.page_number = 1
            mock_chunk.metadata = {}

            retriever_service._load_chunks_by_chunk_ids = AsyncMock(
                return_value={
                    "chunk1": mock_chunk,
                }
            )

            # Execute
            results = await retriever_service.retrieve("test query", top_k=1)

            # Verify - should only use semantic search
            assert len(results) == 1

    def test_merge_results_normalization(self, retriever_service):
        """Test that keyword scores are normalized to 0-1 range."""
        semantic_results = [
            MagicMock(vector_id="chunk1", similarity_score=0.8),
        ]
        keyword_results = [
            ("chunk1", 10.0),
            ("chunk2", 5.0),
        ]

        merged = retriever_service._merge_results(semantic_results, keyword_results)

        # Keyword scores should be normalized
        assert "chunk1" in merged
        assert "chunk2" in merged
        assert merged["chunk1"] <= 1.0  # Normalized
        assert merged["chunk2"] <= 1.0  # Normalized

    def test_merge_results_empty(self, retriever_service):
        """Test merging empty results."""
        merged = retriever_service._merge_results([], [])

        assert merged == {}

    def test_merge_results_semantic_only(self, retriever_service):
        """Test merging with only semantic results."""
        semantic_results = [
            MagicMock(vector_id="chunk1", similarity_score=0.9),
            MagicMock(vector_id="chunk2", similarity_score=0.8),
        ]

        merged = retriever_service._merge_results(semantic_results, [])

        assert len(merged) == 2
        assert merged["chunk1"] == 0.9
        assert merged["chunk2"] == 0.8

    def test_merge_results_keyword_only(self, retriever_service):
        """Test merging with only keyword results."""
        keyword_results = [
            ("chunk1", 1.0),
            ("chunk2", 0.5),
        ]

        merged = retriever_service._merge_results([], keyword_results)

        assert len(merged) == 2
        # Should be normalized and boosted
        assert merged["chunk1"] <= 1.2  # Boosted
        assert merged["chunk2"] <= 1.2  # Boosted
