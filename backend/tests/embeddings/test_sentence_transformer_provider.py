"""Tests for SentenceTransformerEmbeddingProvider."""

import numpy as np
import pytest

from app.embeddings.exceptions import EmbeddingGenerationException
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)


class TestSentenceTransformerEmbeddingProvider:
    """Tests for SentenceTransformerEmbeddingProvider."""

    def test_init(self):
        """Test provider initialization."""
        provider = SentenceTransformerEmbeddingProvider()
        assert provider._model_name == "BAAI/bge-small-en-v1.5"
        assert provider._model is None  # Model should be lazy loaded

    def test_init_custom_model(self):
        """Test provider initialization with custom model name."""
        provider = SentenceTransformerEmbeddingProvider(model_name="all-MiniLM-L6-v2")
        assert provider._model_name == "all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_generate_embedding_single_text(self):
        """Test generating embedding for a single text."""
        provider = SentenceTransformerEmbeddingProvider()
        text = "This is a test sentence."

        embedding = await provider.generate_embedding(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == provider.dimension()
        assert len(embedding.shape) == 1  # Should be 1D array

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test that empty text raises an exception."""
        provider = SentenceTransformerEmbeddingProvider()

        with pytest.raises(EmbeddingGenerationException, match="empty text"):
            await provider.generate_embedding("")

    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_only(self):
        """Test that whitespace-only text raises an exception."""
        provider = SentenceTransformerEmbeddingProvider()

        with pytest.raises(EmbeddingGenerationException, match="empty text"):
            await provider.generate_embedding("   ")

    @pytest.mark.asyncio
    async def test_generate_embeddings_multiple_texts(self):
        """Test generating embeddings for multiple texts in batch."""
        provider = SentenceTransformerEmbeddingProvider()
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
        ]

        embeddings = await provider.generate_embeddings(texts)

        assert len(embeddings) == 3
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape[0] == provider.dimension()

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for empty list."""
        provider = SentenceTransformerEmbeddingProvider()

        embeddings = await provider.generate_embeddings([])

        assert embeddings == []

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_empty_texts(self):
        """Test that empty texts are filtered out."""
        provider = SentenceTransformerEmbeddingProvider()
        texts = [
            "Valid text.",
            "",
            "   ",
            "Another valid text.",
        ]

        embeddings = await provider.generate_embeddings(texts)

        # Should only generate embeddings for non-empty texts
        assert len(embeddings) == 2

    @pytest.mark.asyncio
    async def test_generate_embeddings_all_empty(self):
        """Test that all empty texts return empty list."""
        provider = SentenceTransformerEmbeddingProvider()
        texts = ["", "   ", ""]

        embeddings = await provider.generate_embeddings(texts)

        assert embeddings == []

    def test_dimension(self):
        """Test getting the embedding dimension."""
        provider = SentenceTransformerEmbeddingProvider()

        # Dimension should be 384 for BAAI/bge-small-en-v1.5
        dimension = provider.dimension()
        assert dimension == 384

    def test_dimension_lazy_loads_model(self):
        """Test that calling dimension loads the model."""
        provider = SentenceTransformerEmbeddingProvider()

        # Model should be None before calling dimension
        assert provider._model is None

        # Call dimension
        dimension = provider.dimension()

        # Model should now be loaded
        assert provider._model is not None
        assert dimension == 384

    @pytest.mark.asyncio
    async def test_model_caching(self):
        """Test that the model is cached after first load."""
        provider = SentenceTransformerEmbeddingProvider()

        # First call should load the model
        await provider.generate_embedding("Test text.")
        model_after_first = provider._model

        # Second call should reuse the model
        await provider.generate_embedding("Another test.")
        model_after_second = provider._model

        # Model should be the same instance
        assert model_after_first is model_after_second

    @pytest.mark.asyncio
    async def test_embedding_normalization(self):
        """Test that embeddings are normalized."""
        provider = SentenceTransformerEmbeddingProvider()
        text = "Test sentence for normalization."

        embedding = await provider.generate_embedding(text)

        # Calculate L2 norm
        norm = np.linalg.norm(embedding)

        # Should be approximately 1.0 (normalized)
        assert abs(norm - 1.0) < 0.001

    @pytest.mark.asyncio
    async def test_embedding_consistency(self):
        """Test that the same text produces the same embedding."""
        provider = SentenceTransformerEmbeddingProvider()
        text = "Consistency test sentence."

        embedding1 = await provider.generate_embedding(text)
        embedding2 = await provider.generate_embedding(text)

        # Embeddings should be identical
        np.testing.assert_array_almost_equal(embedding1, embedding2)

    @pytest.mark.asyncio
    async def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        provider = SentenceTransformerEmbeddingProvider()
        text1 = "First unique sentence."
        text2 = "Second unique sentence."

        embedding1 = await provider.generate_embedding(text1)
        embedding2 = await provider.generate_embedding(text2)

        # Embeddings should be different
        assert not np.allclose(embedding1, embedding2)

    @pytest.mark.asyncio
    async def test_batch_vs_single_consistency(self):
        """Test that batch generation produces same results as single."""
        provider = SentenceTransformerEmbeddingProvider()
        texts = ["Test sentence 1.", "Test sentence 2."]

        # Generate embeddings in batch
        batch_embeddings = await provider.generate_embeddings(texts)

        # Generate embeddings individually
        single_embeddings = [
            await provider.generate_embedding(texts[0]),
            await provider.generate_embedding(texts[1]),
        ]

        # Should be approximately the same
        for batch, single in zip(batch_embeddings, single_embeddings, strict=False):
            np.testing.assert_array_almost_equal(batch, single)
