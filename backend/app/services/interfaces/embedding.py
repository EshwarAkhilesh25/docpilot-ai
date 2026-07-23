from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract provider interface for text embedding operations.

    This interface defines the contract for generating text embeddings
    across different embedding backends (OpenAI, HuggingFace, etc.).
    Implementations should handle backend-specific details while adhering
    to this interface.
    """

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            EmbeddingError: If embedding generation fails.
        """

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of embedding vectors (list of floats).

        Raises:
            EmbeddingError: If embedding generation fails.
        """

    @abstractmethod
    async def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors.

        Returns:
            The dimension of the embedding vectors.
        """

    @abstractmethod
    async def similarity_search(
        self, query_embedding: list[float], embeddings: list[list[float]], k: int = 5
    ) -> list[tuple[int, float]]:
        """Find the most similar embeddings to a query.

        Args:
            query_embedding: The query embedding vector.
            embeddings: A list of embedding vectors to search.
            k: The number of top results to return.

        Returns:
            A list of tuples containing (index, similarity_score).

        Raises:
            EmbeddingError: If similarity search fails.
        """
