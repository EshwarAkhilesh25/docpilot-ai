"""Interface for Retrieval Strategies."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.document_chunk import DocumentChunk


class RetrievalStrategy(ABC):
    """Abstract interface for retrieving document chunks.

    Different workflows may require different retrieval techniques
    (e.g., semantic search, chronological fetch, full document fetch).
    """

    @abstractmethod
    async def retrieve(
        self,
        question: str,
        document_ids: list[UUID] | None,
        vector_index_service,
        embedding_service,
        uow,
        **kwargs,
    ) -> list[DocumentChunk]:
        """Execute the retrieval strategy.

        Args:
            question: The user's question.
            document_ids: Restrict search to these documents.
            vector_index_service: The vector search service.
            embedding_service: The embedding service.
            uow: The unit of work for database access.
            **kwargs: Additional parameters (e.g., top_k, search_k).

        Returns:
            A list of relevant document chunks.
        """
        pass
