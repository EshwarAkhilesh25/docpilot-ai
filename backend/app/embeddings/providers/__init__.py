"""Embedding provider implementations."""

from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)

__all__ = [
    "SentenceTransformerEmbeddingProvider",
]
