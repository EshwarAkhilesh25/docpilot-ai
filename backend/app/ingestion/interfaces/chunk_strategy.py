from abc import ABC, abstractmethod

from app.ingestion.models import TextChunk


class ChunkStrategy(ABC):
    """Abstract interface for text chunking strategies.

    A ChunkStrategy is responsible for splitting text into smaller chunks
    for processing (e.g., for embedding generation). Different strategies
    can be implemented based on requirements (e.g., semantic chunking,
    fixed-size chunking, etc.).
    """

    @abstractmethod
    def chunk(self, text: str) -> list[TextChunk]:
        """Split text into chunks.

        Args:
            text: The text to chunk.

        Returns:
            List of TextChunk objects containing the chunked text.
        """
        pass
