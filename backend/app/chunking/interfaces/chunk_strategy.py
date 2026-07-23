"""Interface for chunking strategies."""

from abc import ABC, abstractmethod

from app.chunking.models.chunk import Chunk


class ChunkStrategy(ABC):
    """Abstract interface for text chunking strategies.

    This interface defines the contract for splitting text into chunks.
    Different strategies can be implemented (recursive, semantic, fixed-size, etc.).
    """

    @abstractmethod
    def chunk(self, text: str) -> list[Chunk]:
        """Split text into chunks.

        Args:
            text: The text to chunk.

        Returns:
            List of Chunk objects containing the chunked text and metadata.
        """
        pass
