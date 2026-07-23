"""Service for managing keyword index operations.

This service coordinates keyword indexing operations, handling chunk indexing,
deletion, and persistence through the KeywordIndexProvider.
"""

import logging
from uuid import UUID

from app.core.config import get_settings
from app.keyword_search.exceptions.exceptions import KeywordIndexError
from app.keyword_search.interfaces.keyword_index_provider import KeywordIndexProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class KeywordIndexService:
    """Service for managing keyword index operations.

    This service handles the business logic for keyword indexing,
    including adding chunks, removing chunks, and managing index persistence.
    """

    def __init__(self, keyword_index_provider: KeywordIndexProvider):
        """Initialize the keyword index service.

        Args:
            keyword_index_provider: The keyword index provider implementation.
        """
        self._keyword_index_provider = keyword_index_provider
        self._index_path = getattr(settings, "BM25_INDEX_PATH", "storage/bm25_index")

    def initialize_index(self) -> None:
        """Initialize the keyword index.

        This loads the index from disk if available, or creates a new one.

        Raises:
            KeywordIndexError: If initialization fails.
        """
        try:
            from pathlib import Path

            index_file = Path(self._index_path) / "bm25_index.pkl"

            if index_file.exists():
                pass
                self._keyword_index_provider.load_index(str(index_file))
            else:
                pass
                self._keyword_index_provider.create_index()
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to initialize index: {e}")

    def index_chunk(self, chunk_id: UUID, text: str, metadata: dict | None = None) -> None:
        """Index a single chunk.

        Args:
            chunk_id: The unique identifier for the chunk.
            text: The text content to index.
            metadata: Optional metadata associated with the chunk.

        Raises:
            KeywordIndexError: If indexing fails.
        """
        try:
            self._keyword_index_provider.add_chunk(chunk_id, text, metadata)
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to index chunk: {e}")

    def index_chunks(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Index multiple chunks and persist the index.

        Args:
            chunks: List of tuples (chunk_id, text, metadata).

        Raises:
            KeywordIndexError: If indexing fails.
        """
        try:
            # Detailed logging for RAG debugging
            pass

            self._keyword_index_provider.add_chunks(chunks)
            pass

            # Log index size after indexing
            pass

            # Persist index after indexing
            self.save_index()
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to index chunks: {e}")

    def remove_chunk(self, chunk_id: UUID) -> None:
        """Remove a chunk from the index.

        Args:
            chunk_id: The unique identifier for the chunk to remove.

        Raises:
            KeywordIndexError: If removal fails.
        """
        try:
            self._keyword_index_provider.remove_chunk(chunk_id)
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to remove chunk: {e}")

    def remove_chunks(self, chunk_ids: list[UUID]) -> None:
        """Remove multiple chunks from the index.

        Args:
            chunk_ids: List of chunk identifiers to remove.

        Raises:
            KeywordIndexError: If removal fails.
        """
        try:
            self._keyword_index_provider.remove_chunks(chunk_ids)
            pass
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to remove chunks: {e}")

    def rebuild_index(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Rebuild the entire index from scratch.

        Args:
            chunks: List of tuples (chunk_id, text, metadata) to index.

        Raises:
            KeywordIndexError: If rebuilding fails.
        """
        try:
            self._keyword_index_provider.rebuild_index(chunks)
            pass
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to rebuild index: {e}")

    def save_index(self) -> None:
        """Save the index to disk.

        Raises:
            KeywordIndexError: If saving fails.
        """
        try:
            from pathlib import Path

            index_file = Path(self._index_path) / "bm25_index.pkl"
            self._keyword_index_provider.save_index(str(index_file))
            pass
        except Exception as e:
            pass
            raise KeywordIndexError(f"Failed to save index: {e}")

    def get_index_size(self) -> int:
        """Get the number of chunks in the index.

        Returns:
            The number of indexed chunks.
        """
        return self._keyword_index_provider.get_index_size()
