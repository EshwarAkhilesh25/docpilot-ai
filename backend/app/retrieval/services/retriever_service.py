from app.retrieval.models.relevant_chunk import RelevantChunk

"""Retriever service for semantic and hybrid document chunk retrieval."""

import logging
import time
from collections.abc import Callable
from difflib import SequenceMatcher
from uuid import UUID

from app.core.config import get_settings
from app.embeddings.interfaces.embedding_provider import EmbeddingProvider
from app.keyword_search.interfaces.keyword_index_provider import KeywordIndexProvider
from app.retrieval.exceptions import RetrievalException
from app.retrieval.interfaces.retriever import Retriever
from app.vectorstore.interfaces.vector_index_provider import VectorIndexProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class RetrieverService(Retriever):
    """Service for retrieving relevant document chunks using semantic and hybrid search.

    This service implements the retrieval pipeline:
    1. Generate embedding for query
    2. Search vector index for similar vectors (semantic)
    3. Search keyword index for exact matches (lexical)
    4. Merge and rank results from both sources
    5. Load DocumentChunk records for matching IDs
    6. Deduplicate overlapping chunks
    7. Return ranked RelevantChunk objects
    """

    def __init__(
        self,
        uow_factory: Callable,
        embedding_provider: EmbeddingProvider,
        vector_provider: VectorIndexProvider,
        keyword_index_provider: KeywordIndexProvider | None = None,
        deduplication_threshold: float = 0.95,
    ):
        """Initialize the retriever service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            embedding_provider: Provider for generating query embeddings.
            vector_provider: Provider for vector similarity search.
            keyword_index_provider: Optional provider for keyword search.
            deduplication_threshold: Similarity threshold for deduplication (0-1).
        """
        self._uow_factory = uow_factory
        self._embedding_provider = embedding_provider
        self._vector_provider = vector_provider
        self._keyword_index_provider = keyword_index_provider
        self._deduplication_threshold = deduplication_threshold

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
        try:
            start_time = time.time()

            pass

            # Step 1: Generate embedding for query
            query_embedding = await self._embedding_provider.generate_embedding(query)

            # Step 2: Perform semantic search (FAISS)
            semantic_results = await self._vector_provider.search(
                query_embedding, top_k=settings.SEMANTIC_TOP_K
            )
            {result.vector_id for result in semantic_results}

            # Detailed logging for semantic results
            pass

            # Step 3: Perform keyword search (BM25) if enabled
            keyword_results = []
            if settings.HYBRID_RETRIEVAL_ENABLED and self._keyword_index_provider:
                keyword_results = self._keyword_index_provider.search(
                    query, top_k=settings.KEYWORD_TOP_K
                )

                # Detailed logging for keyword results
                pass

            # Step 4: Merge semantic and keyword results
            merged_results = self._merge_results(semantic_results, keyword_results)  # type: ignore

            if not merged_results:
                pass
                return []

            # Step 5: Load DocumentChunk records (batch)
            chunk_ids_to_load = list(merged_results.keys())

            # Detailed logging for database lookup
            pass

            chunks_dict = await self._load_chunks_by_chunk_ids(chunk_ids_to_load)  # type: ignore

            # Detailed logging for lookup results
            pass

            # Step 6: Build RelevantChunk objects with similarity scores
            relevant_chunks: list[RelevantChunk] = []
            for chunk_id, score in merged_results.items():
                chunk = chunks_dict.get(chunk_id)  # type: ignore
                if chunk is None:
                    # Stale chunk ID - chunk was deleted
                    pass
                    continue

                # Filter by document_ids if provided
                if document_ids and chunk.document_id not in document_ids:
                    continue

                relevant_chunk = RelevantChunk(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    similarity_score=score,
                    start_page=chunk.page_number,
                    end_page=chunk.page_number,
                    metadata=chunk.chunk_metadata,
                )
                relevant_chunks.append(relevant_chunk)

            # Step 7: Deduplicate overlapping chunks
            deduplicated_chunks = self._deduplicate_chunks(relevant_chunks)

            # Step 8: Return top_k results
            final_results = deduplicated_chunks[:top_k]

            time.time() - start_time

            pass

            return final_results

        except Exception as e:
            if "Index has not been created" in str(e):
                pass
                return []
            pass
            raise RetrievalException(f"Retrieval failed: {e}")

    def _merge_results(
        self,
        semantic_results: list,
        keyword_results: list[tuple[str, float]],
    ) -> dict[UUID, float]:
        """Merge semantic and keyword search results.

        Args:
            semantic_results: List of semantic search results with vector_id and similarity.
            keyword_results: List of keyword search results (chunk_id, score).

        Returns:
            Dictionary mapping chunk_id to highest score.
        """
        merged: dict[UUID, float] = {}

        # Add semantic results with weight
        for result in semantic_results:
            chunk_id = result.vector_id
            score = result.similarity_score * settings.SEMANTIC_WEIGHT
            if chunk_id not in merged or score > merged[chunk_id]:
                merged[chunk_id] = score

        # Add keyword results with weight (normalize scores to 0-1 range)
        if keyword_results:
            max_keyword_score = (
                max(score for _, score in keyword_results) if keyword_results else 1.0
            )
            for chunk_id, score in keyword_results:
                # Normalize keyword score to 0-1 range
                normalized_score = score / max_keyword_score if max_keyword_score > 0 else 0.0
                # Apply configurable weight
                weighted_score = normalized_score * settings.KEYWORD_WEIGHT
                if chunk_id not in merged or weighted_score > merged[chunk_id]:  # type: ignore
                    merged[chunk_id] = weighted_score  # type: ignore

        # Sort by score (descending) and return top merged results
        sorted_results = dict(sorted(merged.items(), key=lambda x: x[1], reverse=True))

        # Limit to merged_top_k
        top_results = dict(list(sorted_results.items())[: settings.MERGED_TOP_K])

        return top_results

    async def _load_chunks_by_chunk_ids(self, chunk_ids: list[str]) -> dict[str, any]:  # type: ignore
        """Load DocumentChunk records by vector IDs (batch).

        Args:
            chunk_ids: List of vector IDs to load.

        Returns:
            Dictionary mapping vector_id to DocumentChunk.
        """
        chunks = {}

        uow = self._uow_factory()
        async with uow:
            try:
                # Batch load all chunks at once by vector_id
                chunk_list = await uow.document_chunk_repository.get_by_vector_ids(chunk_ids)
                # Build dictionary
                for chunk in chunk_list:
                    chunks[chunk.vector_id] = chunk
            except Exception:
                pass
                # Fallback to individual loading
                for chunk_id in chunk_ids:
                    try:
                        chunk = await uow.document_chunk_repository.get_by_vector_id(chunk_id)
                        if chunk:
                            chunks[chunk_id] = chunk
                    except Exception:
                        pass
                        continue

        return chunks

    def _deduplicate_chunks(self, chunks: list[RelevantChunk]) -> list[RelevantChunk]:
        """Deduplicate overlapping chunks based on similarity and content.

        Args:
            chunks: List of RelevantChunk objects to deduplicate.

        Returns:
            Deduplicated list of RelevantChunk objects.
        """
        if len(chunks) <= 1:
            return chunks

        deduplicated: list[RelevantChunk] = []
        seen_chunks: set[UUID] = set()

        for chunk in chunks:
            # Check for exact duplicates (same document and chunk_index)
            chunk_key = (chunk.document_id, chunk.chunk_index)
            if chunk_key in seen_chunks:
                continue

            # Check for near-duplicates based on similarity score
            # If similarity is very high (> threshold), it's likely the same content
            is_duplicate = False
            for existing_chunk in deduplicated:
                if (
                    chunk.document_id == existing_chunk.document_id
                    and chunk.chunk_index == existing_chunk.chunk_index
                ):
                    is_duplicate = True
                    break

                # Check for overlapping content (similar text)
                if self._are_chunks_overlapping(chunk, existing_chunk):
                    # Keep the one with higher similarity score
                    if chunk.similarity_score > existing_chunk.similarity_score:
                        deduplicated.remove(existing_chunk)
                        seen_chunks.remove((existing_chunk.document_id, existing_chunk.chunk_index))  # type: ignore
                    else:
                        is_duplicate = True
                        break

            if not is_duplicate:
                deduplicated.append(chunk)
                seen_chunks.add(chunk_key)  # type: ignore

        return deduplicated

    def _are_chunks_overlapping(self, chunk1: RelevantChunk, chunk2: RelevantChunk) -> bool:
        """Check if two chunks have overlapping content using token similarity.

        Args:
            chunk1: First chunk.
            chunk2: Second chunk.

        Returns:
            True if chunks overlap significantly (similarity > threshold).
        """
        # If they're from different documents, they don't overlap
        if chunk1.document_id != chunk2.document_id:
            return False

        # If they're the same chunk index, they're duplicates
        if chunk1.chunk_index == chunk2.chunk_index:
            return True

        # Use SequenceMatcher for token-level similarity
        text1 = chunk1.text
        text2 = chunk2.text

        if not text1 or not text2:
            return False

        # Calculate similarity ratio (0.0 to 1.0)
        similarity = SequenceMatcher(None, text1, text2).ratio()

        # Consider overlapping if similarity exceeds threshold
        return similarity > self._deduplication_threshold
