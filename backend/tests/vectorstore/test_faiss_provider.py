"""Tests for FAISSVectorProvider."""

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest

from app.vectorstore.exceptions import (
    DuplicateVectorException,
    VectorDimensionMismatchException,
    VectorIndexException,
    VectorIndexNotFoundException,
)
from app.vectorstore.models.search_result import SearchResult
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider


class TestFAISSVectorProvider:
    """Tests for FAISSVectorProvider."""

    @pytest.mark.asyncio
    async def test_create_index(self):
        """Test creating a new index."""
        provider = FAISSVectorProvider()

        await provider.create_index(dimension=384)

        assert provider.dimension() == 384

    @pytest.mark.asyncio
    async def test_create_empty_index(self):
        """Test creating an index and checking it's empty."""
        provider = FAISSVectorProvider()

        await provider.create_index(dimension=128)

        # Search should return empty results
        query = np.random.rand(128).astype(np.float32)
        results = await provider.search(query, top_k=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_add_vectors(self):
        """Test adding vectors to the index."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = ["vec1", "vec2", "vec3"]
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(3)]

        await provider.add_vectors(vector_ids, vectors)

        # Should be able to search now
        query = vectors[0]
        results = await provider.search(query, top_k=3)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_add_vectors_dimension_mismatch(self):
        """Test that adding vectors with wrong dimension raises exception."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = ["vec1"]
        vectors = [np.random.rand(256).astype(np.float32)]  # Wrong dimension

        with pytest.raises(VectorDimensionMismatchException):
            await provider.add_vectors(vector_ids, vectors)

    @pytest.mark.asyncio
    async def test_add_duplicate_vector_ids(self):
        """Test that duplicate vector IDs raise exception."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        # Add a vector first
        await provider.add_vectors(["vec1"], [np.random.rand(128).astype(np.float32)])

        vector_ids = ["vec1", "vec2"]  # Duplicate
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(2)]

        with pytest.raises(DuplicateVectorException):
            await provider.add_vectors(vector_ids, vectors)

    @pytest.mark.asyncio
    async def test_search_without_index(self):
        """Test that searching without index raises exception."""
        provider = FAISSVectorProvider()

        query = np.random.rand(128).astype(np.float32)

        with pytest.raises(VectorIndexNotFoundException):
            await provider.search(query, top_k=5)

    @pytest.mark.asyncio
    async def test_search_dimension_mismatch(self):
        """Test that searching with wrong dimension raises exception."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        # Add a vector so ntotal > 0
        await provider.add_vectors(["vec1"], [np.random.rand(128).astype(np.float32)])

        query = np.random.rand(256).astype(np.float32)  # Wrong dimension

        with pytest.raises(VectorDimensionMismatchException):
            await provider.search(query, top_k=5)

    @pytest.mark.asyncio
    async def test_search_returns_correct_structure(self):
        """Test that search returns SearchResult objects."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = ["vec1", "vec2"]
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(2)]
        await provider.add_vectors(vector_ids, vectors)

        query = vectors[0]
        results = await provider.search(query, top_k=2)

        assert len(results) > 0
        for result in results:
            assert isinstance(result, SearchResult)
            assert isinstance(result.vector_id, str)
            assert isinstance(result.similarity_score, float)

    @pytest.mark.asyncio
    async def test_search_top_k(self):
        """Test that search respects top_k parameter."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = [f"vec{i}" for i in range(10)]
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(10)]
        await provider.add_vectors(vector_ids, vectors)

        query = vectors[0]
        results = await provider.search(query, top_k=3)

        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_delete_vectors(self):
        """Test deleting vectors from the index."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = ["vec1", "vec2", "vec3"]
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(3)]
        await provider.add_vectors(vector_ids, vectors)

        # Delete one vector
        await provider.delete_vectors(["vec1"])

        # Search should still work
        query = vectors[0]
        results = await provider.search(query, top_k=3)

        # vec1 should not be in results (removed from mapping)
        assert not any(r.vector_id == "vec1" for r in results)

    @pytest.mark.asyncio
    async def test_delete_vectors_without_index(self):
        """Test that deleting without index raises exception."""
        provider = FAISSVectorProvider()

        with pytest.raises(VectorIndexNotFoundException):
            await provider.delete_vectors(["vec1"])

    @pytest.mark.asyncio
    async def test_persistence_save_and_load(self):
        """Test saving and loading the index."""
        with TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.faiss"

            # Create and populate index
            provider1 = FAISSVectorProvider()
            await provider1.create_index(dimension=128)

            vector_ids = ["vec1", "vec2"]
            vectors = [np.random.rand(128).astype(np.float32) for _ in range(2)]
            await provider1.add_vectors(vector_ids, vectors)

            # Save
            await provider1.save(str(index_path))

            # Load in new provider
            provider2 = FAISSVectorProvider()
            await provider2.load(str(index_path))

            # Should have same dimension
            assert provider2.dimension() == 128

            # Should be able to search
            query = vectors[0]
            results = await provider2.search(query, top_k=2)

            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_persistence_load_nonexistent(self):
        """Test that loading nonexistent file raises exception."""
        provider = FAISSVectorProvider()

        with pytest.raises(VectorIndexNotFoundException):
            await provider.load("/nonexistent/path/index.faiss")

    @pytest.mark.asyncio
    async def test_persistence_save_without_index(self):
        """Test that saving without index raises exception."""
        provider = FAISSVectorProvider()

        with pytest.raises(VectorIndexNotFoundException):
            await provider.save("/tmp/index.faiss")

    @pytest.mark.asyncio
    async def test_auto_load_on_init(self):
        """Test that index is auto-loaded if path exists."""
        with TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.faiss"

            # Create and save index
            provider1 = FAISSVectorProvider()
            await provider1.create_index(dimension=128)

            vector_ids = ["vec1"]
            vectors = [np.random.rand(128).astype(np.float32)]
            await provider1.add_vectors(vector_ids, vectors)
            await provider1.save(str(index_path))

            # Create new provider with path - should auto-load
            provider2 = FAISSVectorProvider(index_path=str(index_path))

            # Should have index loaded
            assert provider2.dimension() == 128

    @pytest.mark.asyncio
    async def test_batch_vector_insertion(self):
        """Test batch insertion of many vectors."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        # Insert 100 vectors
        vector_ids = [f"vec{i}" for i in range(100)]
        vectors = [np.random.rand(128).astype(np.float32) for _ in range(100)]

        await provider.add_vectors(vector_ids, vectors)

        # Search should work
        query = vectors[0]
        results = await provider.search(query, top_k=10)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_empty_vector_list(self):
        """Test adding empty list of vectors."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        await provider.add_vectors([], [])

        # Should not raise exception

    @pytest.mark.asyncio
    async def test_mismatched_vector_count(self):
        """Test that mismatched vector ID and vector counts raise exception."""
        provider = FAISSVectorProvider()
        await provider.create_index(dimension=128)

        vector_ids = ["vec1", "vec2"]
        vectors = [np.random.rand(128).astype(np.float32)]  # Only one vector

        with pytest.raises(VectorIndexException):
            await provider.add_vectors(vector_ids, vectors)

    @pytest.mark.asyncio
    async def test_dimension_without_index(self):
        """Test that getting dimension without index raises exception."""
        provider = FAISSVectorProvider()

        with pytest.raises(VectorIndexNotFoundException):
            provider.dimension()
