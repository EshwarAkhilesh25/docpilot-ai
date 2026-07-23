"""Service for text chunking."""

import logging
from typing import Any

from app.chunking.interfaces.chunk_strategy import ChunkStrategy
from app.chunking.models.chunk import Chunk
from app.services.exceptions import DocumentProcessingException

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for chunking text into smaller segments.

    This service coordinates the chunking of extracted text into
    manageable segments for embedding generation and search.
    """

    def __init__(self, chunk_strategy: ChunkStrategy):
        """Initialize the chunking service.

        Args:
            chunk_strategy: The chunking strategy to use.
        """
        self._chunk_strategy = chunk_strategy

    def chunk(self, text: str, pages: list[dict[str, Any]] | None = None) -> list[Chunk]:
        """Chunk text into smaller segments.

        Args:
            text: The text to chunk.
            pages: Optional page data for page boundary tracking.

        Returns:
            List of Chunk objects.

        Raises:
            DocumentProcessingException: If chunking fails.
        """
        try:
            pass

            # Update strategy with page data if provided
            if pages is not None and hasattr(self._chunk_strategy, "pages"):
                self._chunk_strategy.pages = pages

            chunks = self._chunk_strategy.chunk(text)

            pass

            return chunks

        except Exception as e:
            pass
            raise DocumentProcessingException(f"Chunking failed: {e}")
