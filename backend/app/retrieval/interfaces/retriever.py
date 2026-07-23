"""Interface for semantic retrievers."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.retrieval.models.relevant_chunk import RelevantChunk


class Retriever(ABC):
    """Abstract interface for semantic retrievers.

    This interface defines the contract for retrieving relevant document chunks
    based on semantic similarity to a query. Different implementations can use
    different strategies (vector search, hybrid search, reranking, etc.).
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        search_k: int = 20,
        document_ids: list[UUID] | None = None,
    ) -> list[RelevantChunk]:
        """Retrieve the most relevant document chunks for a query.

        Args:
            query: The user's search query.
            top_k: Number of relevant chunks to return after deduplication.
            search_k: Number of chunks to retrieve from vector search before deduplication.
            document_ids: Optional list of document IDs to filter results.

        Returns:
            List of RelevantChunk objects ranked by relevance.

        Raises:
            RetrievalException: If retrieval fails.
        """
        pass
