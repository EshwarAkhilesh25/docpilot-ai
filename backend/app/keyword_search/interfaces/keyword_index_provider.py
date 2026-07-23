"""Interface for keyword index providers.

This module defines the abstraction for lexical search providers,
allowing different implementations (BM25, Elasticsearch, etc.) to be swapped.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class KeywordIndexProvider(ABC):
    """Abstract base class for keyword index providers.

    This interface defines the contract for lexical search implementations.
    Providers must support indexing, searching, deletion, and persistence.
    """

    @abstractmethod
    def create_index(self) -> None:
        """Create a new keyword index.

        Raises:
            KeywordIndexError: If index creation fails.
        """
        pass

    @abstractmethod
    def add_chunk(self, chunk_id: UUID, text: str, metadata: dict | None = None) -> None:
        """Add a chunk to the keyword index.

        Args:
            chunk_id: The unique identifier for the chunk.
            text: The text content to index.
            metadata: Optional metadata associated with the chunk.

        Raises:
            KeywordIndexError: If adding the chunk fails.
        """
        pass

    @abstractmethod
    def add_chunks(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Add multiple chunks to the keyword index.

        Args:
            chunks: List of tuples (chunk_id, text, metadata).

        Raises:
            KeywordIndexError: If adding chunks fails.
        """
        pass

    @abstractmethod
    def remove_chunk(self, chunk_id: UUID) -> None:
        """Remove a chunk from the keyword index.

        Args:
            chunk_id: The unique identifier for the chunk to remove.

        Raises:
            KeywordIndexError: If removal fails.
        """
        pass

    @abstractmethod
    def remove_chunks(self, chunk_ids: list[UUID]) -> None:
        """Remove multiple chunks from the keyword index.

        Args:
            chunk_ids: List of chunk identifiers to remove.

        Raises:
            KeywordIndexError: If removal fails.
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[tuple[UUID, float]]:
        """Search the keyword index for relevant chunks.

        Args:
            query: The search query text.
            top_k: Maximum number of results to return.

        Returns:
            List of tuples (chunk_id, score) sorted by relevance (highest first).

        Raises:
            KeywordIndexError: If search fails.
        """
        pass

    @abstractmethod
    def save_index(self, path: str) -> None:
        """Save the keyword index to disk.

        Args:
            path: The file path where the index should be saved.

        Raises:
            KeywordIndexError: If saving fails.
        """
        pass

    @abstractmethod
    def load_index(self, path: str) -> None:
        """Load the keyword index from disk.

        Args:
            path: The file path from which to load the index.

        Raises:
            KeywordIndexError: If loading fails.
        """
        pass

    @abstractmethod
    def rebuild_index(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Rebuild the entire keyword index from scratch.

        This clears the existing index and re-indexes all provided chunks.

        Args:
            chunks: List of tuples (chunk_id, text, metadata) to index.

        Raises:
            KeywordIndexError: If rebuilding fails.
        """
        pass

    @abstractmethod
    def get_index_size(self) -> int:
        """Get the number of chunks in the index.

        Returns:
            The number of indexed chunks.
        """
        pass
