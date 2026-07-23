from uuid import UUID

"""BM25 provider for keyword search.

This module implements the KeywordIndexProvider interface using the rank-bm25 library.
It provides lexical search capabilities for exact keyword matching.
"""

import logging
import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.keyword_search.exceptions.exceptions import (
    KeywordIndexCreationError,
    KeywordIndexPersistenceError,
    KeywordIndexSearchError,
)
from app.keyword_search.interfaces.keyword_index_provider import KeywordIndexProvider

logger = logging.getLogger(__name__)


class BM25Provider(KeywordIndexProvider):
    """BM25-based keyword index provider.

    This provider uses the BM25Okapi algorithm for lexical search.
    It maintains an in-memory index with optional disk persistence.
    """

    def __init__(self, index_path: str | None = None):
        """Initialize the BM25 provider.

        Args:
            index_path: Optional path to load/save the index from/to disk.
        """
        self._index_path = index_path
        self._corpus: list[str] = []
        self._chunk_ids: list[str] = []
        self._metadata: dict[str, dict] = {}
        self._chunk_id_to_index: dict[str, int] = {}
        self._bm25_index: BM25Okapi | None = None
        self._index_size = 0

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization for BM25.

        Args:
            text: The text to tokenize.

        Returns:
            List of tokens.
        """
        # Simple whitespace and punctuation tokenization
        import re

        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens

    def create_index(self) -> None:
        """Create a new BM25 index.

        Raises:
            KeywordIndexCreationError: If index creation fails.
        """
        try:
            self._corpus = []
            self._chunk_ids = []
            self._metadata = {}
            self._chunk_id_to_index = {}
            self._bm25_index = None
            self._index_size = 0
            pass
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to create BM25 index: {e}")

    def add_chunk(self, chunk_id: UUID, text: str, metadata: dict | None = None) -> None:
        """Add a chunk to the BM25 index.

        Args:
            chunk_id: The unique identifier for the chunk.
            text: The text content to index.
            metadata: Optional metadata associated with the chunk.

        Raises:
            KeywordIndexCreationError: If adding the chunk fails.
        """
        try:
            chunk_id_str = str(chunk_id)
            if chunk_id_str in self._chunk_id_to_index:
                pass
                return

            index = len(self._corpus)
            self._corpus.append(text)
            self._chunk_ids.append(chunk_id_str)
            self._chunk_id_to_index[chunk_id_str] = index
            if metadata:
                self._metadata[chunk_id_str] = metadata
            self._index_size += 1
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to add chunk: {e}")

    def add_chunks(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Add multiple chunks to the BM25 index.

        Args:
            chunks: List of tuples (chunk_id, text, metadata).

        Raises:
            KeywordIndexCreationError: If adding chunks fails.
        """
        try:
            for chunk_id, text, metadata in chunks:
                self.add_chunk(chunk_id, text, metadata)
            pass
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to add chunks: {e}")

    def remove_chunk(self, chunk_id: UUID) -> None:
        """Remove a chunk from the BM25 index.

        Args:
            chunk_id: The unique identifier for the chunk to remove.

        Raises:
            KeywordIndexCreationError: If removal fails.
        """
        try:
            chunk_id_str = str(chunk_id)
            if chunk_id_str not in self._chunk_id_to_index:
                pass
                return

            # For BM25, we need to rebuild the index after removal
            # This is a limitation of the rank-bm25 library
            index = self._chunk_id_to_index[chunk_id_str]
            del self._corpus[index]
            del self._chunk_ids[index]
            del self._chunk_id_to_index[chunk_id_str]
            if chunk_id_str in self._metadata:
                del self._metadata[chunk_id_str]

            # Rebuild index mapping
            self._chunk_id_to_index = {cid: i for i, cid in enumerate(self._chunk_ids)}

            # Rebuild BM25 index if it exists
            if self._bm25_index is not None:
                self._rebuild_bm25_index()

            self._index_size = len(self._corpus)
            pass
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to remove chunk: {e}")

    def remove_chunks(self, chunk_ids: list[UUID]) -> None:
        """Remove multiple chunks from the BM25 index.

        Args:
            chunk_ids: List of chunk identifiers to remove.

        Raises:
            KeywordIndexCreationError: If removal fails.
        """
        try:
            for chunk_id in chunk_ids:
                self.remove_chunk(chunk_id)
            pass
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to remove chunks: {e}")

    def _rebuild_bm25_index(self) -> None:
        """Rebuild the BM25 index from the current corpus."""
        if not self._corpus:
            self._bm25_index = None
            return

        tokenized_corpus = [self._tokenize(doc) for doc in self._corpus]
        self._bm25_index = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 10) -> list[tuple[UUID, float]]:
        """Search the BM25 index for relevant chunks.

        Args:
            query: The search query text.
            top_k: Maximum number of results to return.

        Returns:
            List of tuples (chunk_id, score) sorted by relevance (highest first).

        Raises:
            KeywordIndexSearchError: If search fails.
        """
        try:
            if self._bm25_index is None:
                self._rebuild_bm25_index()

            if self._bm25_index is None or not self._corpus:
                pass
                return []

            tokenized_query = self._tokenize(query)
            scores = self._bm25_index.get_scores(tokenized_query)

            # Get top-k indices
            import numpy as np

            top_indices = np.argsort(scores)[::-1][:top_k]

            # Convert to chunk IDs and scores
            results = [
                (UUID(self._chunk_ids[i]), float(scores[i]))
                for i in top_indices
                if scores[i] > 0  # Only return results with positive scores
            ]

            return results
        except Exception as e:
            pass
            raise KeywordIndexSearchError(f"Search failed: {e}")

    def save_index(self, path: str) -> None:
        """Save the BM25 index to disk.

        Args:
            path: The file path where the index should be saved.

        Raises:
            KeywordIndexPersistenceError: If saving fails.
        """
        try:
            # Rebuild index before saving to ensure it's up to date
            if self._corpus:
                self._rebuild_bm25_index()

            index_data = {
                "corpus": self._corpus,
                "chunk_ids": self._chunk_ids,
                "metadata": self._metadata,
                "chunk_id_to_index": self._chunk_id_to_index,
                "bm25_index": self._bm25_index,
                "index_size": self._index_size,
            }

            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as f:
                pickle.dump(index_data, f)

            pass
        except Exception as e:
            pass
            raise KeywordIndexPersistenceError(f"Failed to save index: {e}")

    def load_index(self, path: str) -> None:
        """Load the BM25 index from disk.

        Args:
            path: The file path from which to load the index.

        Raises:
            KeywordIndexPersistenceError: If loading fails.
        """
        try:
            if not Path(path).exists():
                pass
                self.create_index()
                return

            with open(path, "rb") as f:
                index_data = pickle.load(f)

            self._corpus = index_data.get("corpus", [])
            self._chunk_ids = index_data.get("chunk_ids", [])
            self._metadata = index_data.get("metadata", {})
            self._chunk_id_to_index = index_data.get("chunk_id_to_index", {})
            self._bm25_index = index_data.get("bm25_index")
            self._index_size = index_data.get("index_size", len(self._corpus))

            pass
        except Exception as e:
            pass
            raise KeywordIndexPersistenceError(f"Failed to load index: {e}")

    def rebuild_index(self, chunks: list[tuple[UUID, str, dict | None]]) -> None:
        """Rebuild the entire BM25 index from scratch.

        Args:
            chunks: List of tuples (chunk_id, text, metadata) to index.

        Raises:
            KeywordIndexCreationError: If rebuilding fails.
        """
        try:
            self.create_index()
            self.add_chunks(chunks)
            self._rebuild_bm25_index()
            pass
        except Exception as e:
            pass
            raise KeywordIndexCreationError(f"Failed to rebuild index: {e}")

    def get_index_size(self) -> int:
        """Get the number of chunks in the index.

        Returns:
            The number of indexed chunks.
        """
        return self._index_size
