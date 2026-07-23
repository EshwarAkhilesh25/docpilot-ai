"""Interface for vector index providers."""

from abc import ABC, abstractmethod

import numpy as np

from app.vectorstore.models.search_result import SearchResult


class VectorIndexProvider(ABC):
    """Abstract interface for vector index providers.

    This interface defines the contract for vector indexing and search operations.
    Different implementations can use different backends (FAISS, Milvus, Weaviate, etc.).
    """

    @abstractmethod
    async def create_index(self, dimension: int) -> None:
        """Create a new vector index.

        Args:
            dimension: The dimension of the vectors to be indexed.

        Raises:
            VectorIndexException: If index creation fails.
        """
        pass

    @abstractmethod
    async def add_vectors(self, vector_ids: list[str], vectors: list[np.ndarray]) -> None:
        """Add vectors to the index.

        Args:
            vector_ids: List of unique identifiers for the vectors.
            vectors: List of embedding vectors to add.

        Raises:
            VectorDimensionMismatchException: If vector dimensions don't match index.
            DuplicateVectorException: If vector IDs already exist.
            VectorIndexException: If addition fails.
        """
        pass

    @abstractmethod
    async def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[SearchResult]:
        """Search for similar vectors.

        Args:
            query_vector: The query embedding vector.
            top_k: Number of results to return.

        Returns:
            List of SearchResult objects with vector IDs and similarity scores.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
            VectorDimensionMismatchException: If query dimension doesn't match index.
            VectorIndexException: If search fails.
        """
        pass

    @abstractmethod
    async def delete_vectors(self, vector_ids: list[str]) -> None:
        """Delete vectors from the index.

        Args:
            vector_ids: List of vector IDs to delete.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
            VectorIndexException: If deletion fails.
        """
        pass

    @abstractmethod
    async def save(self, path: str) -> None:
        """Save the index to disk.

        Args:
            path: The path where to save the index.

        Raises:
            VectorIndexException: If save fails.
        """
        pass

    @abstractmethod
    async def load(self, path: str) -> None:
        """Load the index from disk.

        Args:
            path: The path from which to load the index.

        Raises:
            VectorIndexNotFoundException: If index file doesn't exist.
            VectorIndexException: If load fails.
        """
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Get the dimension of the index.

        Returns:
            The dimension of vectors in the index.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
        """
        pass
