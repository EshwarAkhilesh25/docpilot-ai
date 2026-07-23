"""Standard Hybrid Retrieval Strategy (FAISS + Keyword if available)."""

import logging
from uuid import UUID

from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)


class HybridRetrievalStrategy(RetrievalStrategy):
    """Retrieves document chunks using semantic similarity."""

    async def retrieve(
        self,
        question: str,
        document_ids: list[UUID] | None,
        vector_index_service,
        embedding_service,
        uow,
        **kwargs,
    ) -> list[DocumentChunk]:
        """Perform semantic retrieval."""
        top_k = kwargs.get("top_k", 5)

        # 1. Generate query embedding
        query_embedding = await embedding_service.generate_embeddings([question])
        if not query_embedding or len(query_embedding) == 0:
            return []

        # 2. Search vector index
        semantic_results = await vector_index_service.search(
            query_embedding[0], top_k=kwargs.get("search_k", 20)
        )

        if not semantic_results:
            return []

        # 3. Get matching chunks
        vector_ids = [result.vector_id for result in semantic_results]
        async with uow:
            chunks = await uow.document_chunk_repository.get_by_vector_ids(vector_ids)

        # 4. Filter by document IDs if specified
        if document_ids:
            doc_id_strs = [str(did) for did in document_ids]
            chunks = [chunk for chunk in chunks if str(chunk.document_id) in doc_id_strs]

        # 5. Sort by relevance and take top_k
        chunk_map = {chunk.vector_id: chunk for chunk in chunks}
        sorted_chunks = []
        for result in semantic_results:
            if result.vector_id in chunk_map:
                chunk = chunk_map[result.vector_id]
                # Attach similarity_score for orchestrator
                chunk.similarity_score = getattr(result, "score", 0.0)
                if hasattr(result, "similarity_score"):
                    chunk.similarity_score = result.similarity_score
                sorted_chunks.append(chunk)

        return sorted_chunks[:top_k]
