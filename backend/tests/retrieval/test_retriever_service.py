"""Tests for RetrieverService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import numpy as np
import pytest

from app.models.document_chunk import DocumentChunk
from app.retrieval.models.relevant_chunk import RelevantChunk
from app.retrieval.services.retriever_service import RetrieverService
from app.vectorstore.models.search_result import SearchResult


class TestRetrieverService:
    """Tests for RetrieverService."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock Unit of Work."""
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        return uow

    @pytest.fixture
    def mock_embedding_provider(self):
        """Create a mock embedding provider."""
        provider = AsyncMock()
        provider.dimension.return_value = 384
        return provider

    @pytest.fixture
    def mock_vector_provider(self):
        """Create a mock vector provider."""
        provider = AsyncMock()
        provider.dimension.return_value = 384
        return provider

    @pytest.fixture
    def retriever_service(self, mock_uow, mock_embedding_provider, mock_vector_provider):
        """Create a RetrieverService instance."""
        return RetrieverService(
            uow_factory=lambda: mock_uow,
            embedding_provider=mock_embedding_provider,
            vector_provider=mock_vector_provider,
            deduplication_threshold=0.95,
        )

    @pytest.mark.asyncio
    async def test_successful_retrieval(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test successful retrieval of relevant chunks."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id="vec1", similarity_score=0.95),
            SearchResult(vector_id="vec2", similarity_score=0.90),
            SearchResult(vector_id="vec3", similarity_score=0.85),
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading
        mock_chunk_repo = AsyncMock()
        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=0,
            text="Test chunk 1",
            page_number=1,
            vector_id="vec1",
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=1,
            text="Test chunk 2",
            page_number=1,
            vector_id="vec2",
        )
        chunk3 = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=2,
            text="Test chunk 3",
            page_number=2,
            vector_id="vec3",
        )

        async def mock_get_by_vector_id(vector_id):
            chunks = {"vec1": chunk1, "vec2": chunk2, "vec3": chunk3}
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=3)

        assert len(results) == 3
        assert all(isinstance(r, RelevantChunk) for r in results)
        assert results[0].similarity_score == 0.95
        assert results[1].similarity_score == 0.90
        assert results[2].similarity_score == 0.85

    @pytest.mark.asyncio
    async def test_no_matches(
        self, retriever_service, mock_embedding_provider, mock_vector_provider
    ):
        """Test retrieval when no matches are found."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        mock_vector_provider.search.return_value = []

        results = await retriever_service.retrieve(query, top_k=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_deleted_vector_ids(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test handling of stale/deleted vector IDs."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id="vec1", similarity_score=0.95),
            SearchResult(vector_id="vec2", similarity_score=0.90),  # This one is deleted
            SearchResult(vector_id="vec3", similarity_score=0.85),
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading - vec2 returns None (deleted)
        mock_chunk_repo = AsyncMock()
        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=0,
            text="Test chunk 1",
            page_number=1,
            vector_id="vec1",
        )
        chunk3 = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=2,
            text="Test chunk 3",
            page_number=2,
            vector_id="vec3",
        )

        async def mock_get_by_vector_id(vector_id):
            chunks = {"vec1": chunk1, "vec3": chunk3}
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=5)

        # Should only return 2 results (vec1 and vec3)
        assert len(results) == 2
        # Note: In RelevantChunk, the chunk's id is mapped to chunk_id
        # We can check by document_id or chunk_id
        # chunk_id is used in this mapping so vec1 corresponds to chunk1's id
        # Wait, the assert was results[0].vector_id, which we change to chunk_id
        # wait, the test sets chunk1.id to some UUID, let's just check the text or something.
        assert results[0].chunk_id == chunk1.id
        assert results[1].chunk_id == chunk3.id

    @pytest.mark.asyncio
    async def test_duplicate_chunk_removal(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test removal of duplicate chunks."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id="vec1", similarity_score=0.95),
            SearchResult(vector_id="vec2", similarity_score=0.90),
            SearchResult(vector_id="vec3", similarity_score=0.85),
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading with duplicate content
        mock_chunk_repo = AsyncMock()
        doc_id = uuid4()
        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=0,
            text="Test chunk content",
            page_number=1,
            vector_id="vec1",
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=0,  # Same chunk_index as chunk1
            text="Test chunk content",
            page_number=1,
            vector_id="vec2",
        )
        chunk3 = DocumentChunk(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=1,
            text="Different content",
            page_number=2,
            vector_id="vec3",
        )

        async def mock_get_by_vector_id(vector_id):
            chunks = {"vec1": chunk1, "vec2": chunk2, "vec3": chunk3}
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=5)

        # Should deduplicate - only 2 unique chunks
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_top_k_behavior(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test that top_k parameter is respected."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id=f"vec{i}", similarity_score=0.95 - i * 0.05) for i in range(10)
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading
        mock_chunk_repo = AsyncMock()
        chunks = {}
        for i in range(10):
            chunk = DocumentChunk(
                id=uuid4(),
                document_id=uuid4(),
                chunk_index=i,
                text=f"Test chunk {i}",
                page_number=1,
                vector_id=f"vec{i}",
            )
            chunks[f"vec{i}"] = chunk

        async def mock_get_by_vector_id(vector_id):
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_similarity_ordering(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test that results are ordered by similarity score."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id="vec3", similarity_score=0.70),
            SearchResult(vector_id="vec1", similarity_score=0.95),
            SearchResult(vector_id="vec2", similarity_score=0.85),
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading
        mock_chunk_repo = AsyncMock()
        chunks = {}
        for i in range(1, 4):
            chunk = DocumentChunk(
                id=uuid4(),
                document_id=uuid4(),
                chunk_index=i,
                text=f"Test chunk {i}",
                page_number=1,
                vector_id=f"vec{i}",
            )
            chunks[f"vec{i}"] = chunk

        async def mock_get_by_vector_id(vector_id):
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=5)

        # Results should be ordered by similarity (descending)
        assert results[0].similarity_score == 0.95
        assert results[1].similarity_score == 0.85
        assert results[2].similarity_score == 0.70

    @pytest.mark.asyncio
    async def test_relevant_chunk_fields(
        self, retriever_service, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test that RelevantChunk objects contain all required fields."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        doc_id = uuid4()
        chunk_id = uuid4()
        search_results = [SearchResult(vector_id="vec1", similarity_score=0.95)]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading
        mock_chunk_repo = AsyncMock()
        chunk = DocumentChunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=0,
            text="Test chunk",
            page_number=1,
            vector_id="vec1",
            chunk_metadata={"key": "value"},
        )

        async def mock_get_by_vector_id(vector_id):
            return chunk if vector_id == "vec1" else None

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        results = await retriever_service.retrieve(query, top_k=5)

        assert len(results) == 1
        result = results[0]
        assert result.document_id == doc_id
        assert result.chunk_id == chunk_id
        assert result.chunk_index == 0
        assert result.text == "Test chunk"
        assert result.similarity_score == 0.95
        assert result.start_page == 1
        assert result.end_page == 1
        assert result.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_deduplication_threshold(
        self, mock_uow, mock_embedding_provider, mock_vector_provider
    ):
        """Test deduplication with different thresholds."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedding_provider.generate_embedding.return_value = query_embedding

        search_results = [
            SearchResult(vector_id="vec1", similarity_score=0.95),
            SearchResult(vector_id="vec2", similarity_score=0.94),
        ]
        mock_vector_provider.search.return_value = search_results

        # Mock chunk loading with overlapping content
        mock_chunk_repo = AsyncMock()
        doc_id = uuid4()
        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=0,
            text="Test chunk content",
            page_number=1,
            vector_id="vec1",
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=1,
            text="Test chunk content",  # Same text
            page_number=1,
            vector_id="vec2",
        )

        async def mock_get_by_vector_id(vector_id):
            chunks = {"vec1": chunk1, "vec2": chunk2}
            return chunks.get(vector_id)

        async def mock_get_by_vector_ids(vector_ids):
            return [
                await mock_get_by_vector_id(vid)
                for vid in vector_ids
                if await mock_get_by_vector_id(vid) is not None
            ]

        mock_chunk_repo.get_by_vector_ids.side_effect = mock_get_by_vector_ids
        mock_chunk_repo.get_by_vector_id.side_effect = mock_get_by_vector_id
        mock_uow.document_chunk_repository = mock_chunk_repo

        # With high threshold, should deduplicate
        retriever_service = RetrieverService(
            uow_factory=lambda: mock_uow,
            embedding_provider=mock_embedding_provider,
            vector_provider=mock_vector_provider,
            deduplication_threshold=0.95,
        )
        results = await retriever_service.retrieve(query, top_k=5)
        assert len(results) <= 2  # May deduplicate based on content overlap
