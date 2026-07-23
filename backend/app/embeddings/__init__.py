"""Embedding generation engine for document processing."""

from app.embeddings.interfaces.embedding_provider import EmbeddingProvider
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)

__all__ = [
    "EmbeddingProvider",
    "SentenceTransformerEmbeddingProvider",
]
