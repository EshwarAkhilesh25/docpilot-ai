"""Interface for embedding providers."""

from abc import ABC, abstractmethod

import numpy as np


class EmbeddingProvider(ABC):
    """Abstract interface for embedding generation.

    This interface defines the contract for generating text embeddings.
    Different implementations can use different models (SentenceTransformers, OpenAI, etc.).
    """

    @abstractmethod
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate an embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            A numpy array representing the embedding vector.

        Raises:
            EmbeddingGenerationException: If embedding generation fails.
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed.

        Returns:
            List of numpy arrays representing embedding vectors.

        Raises:
            EmbeddingGenerationException: If embedding generation fails.
        """
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Get the dimension of the embedding vectors.

        Returns:
            The dimension of the embedding vectors.
        """
        pass
