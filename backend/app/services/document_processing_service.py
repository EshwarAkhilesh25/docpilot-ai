"""Document processing service implementation."""

import logging
import time
from collections.abc import Callable
from uuid import UUID, uuid4

from app.db.unit_of_work import IUnitOfWork
from app.keyword_search.services.keyword_index_service import KeywordIndexService
from app.models.document_chunk import DocumentChunk
from app.models.document_content import DocumentContent
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.exceptions import DocumentProcessingException
from app.services.extraction_service import ExtractionService
from app.services.interfaces.document_processing import DocumentProcessingService
from app.services.vector_index_service import VectorIndexService

logger = logging.getLogger(__name__)


class DocumentProcessingServiceImpl(DocumentProcessingService):
    """Implementation of document processing service.

    This service orchestrates the document processing pipeline by coordinating
    specialized services for each stage:
    - ExtractionService: Extract text from documents
    - ChunkingService: Split text into chunks
    - EmbeddingService: Generate embeddings for chunks
    - VectorIndexService: Index embeddings for search

    This service contains no AI implementation logic, only orchestration.
    Each stage is independently Callable and idempotent.
    """

    def __init__(
        self,
        uow_factory: Callable,
        extraction_service: ExtractionService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        vector_index_service: VectorIndexService,
        keyword_index_service: KeywordIndexService | None = None,
        llm_provider=None,
    ):
        """Initialize the document processing service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            extraction_service: Service for text extraction.
            chunking_service: Service for text chunking.
            embedding_service: Service for embedding generation.
            vector_index_service: Service for vector indexing.
            keyword_index_service: Optional service for keyword indexing.
            llm_provider: Optional LLM provider for summarization.
        """
        self._uow_factory = uow_factory
        self._extraction_service = extraction_service
        self._chunking_service = chunking_service
        self._embedding_service = embedding_service
        self._vector_index_service = vector_index_service
        self._keyword_index_service = keyword_index_service
        self._llm_provider = llm_provider

    async def process(self, document_id: UUID) -> None:
        """Process a document through the full pipeline.

        Orchestrates the document processing pipeline:
        1. Load document from database
        2. Extract text using ExtractionService
        3. Summarize using LLMProvider
        4. Store DocumentContent
        5. Chunk text using ChunkingService
        6. Generate embeddings using EmbeddingService
        7. Index vectors using VectorIndexService
        8. Index chunks using KeywordIndexService
        9. Store DocumentChunk records

        Args:
            document_id: The UUID of the document to process.

        Raises:
            DocumentProcessingException: If processing fails.
        """
        try:
            # Stage 1: Extract text
            await self.extract_document(document_id)

            # Stage 2: Summarize document (if LLM provider available)
            if self._llm_provider:
                await self.summarize_document(document_id)
            else:
                pass

            # Stage 3: Chunk text
            chunks = await self.chunk_document(document_id)

            # Stage 4: Generate embeddings
            embeddings = await self.generate_embeddings(document_id, chunks)

            # Stage 5: Index vectors
            await self.index_vectors(document_id, chunks, embeddings)

            # Stage 6: Index chunks for keyword search
            if self._keyword_index_service:
                await self.index_chunks(document_id, chunks)
            else:
                pass

            pass

        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Processing failed: {e}")

    async def generate_ingestion_report(self, document_id: UUID, job_id: UUID) -> None:
        """Generate and store an ingestion report for the job.

        Args:
            document_id: The document UUID.
            job_id: The job UUID.
        """
        uow = self._uow_factory()
        report = {
            "document_id": str(document_id),
            "job_id": str(job_id),
            "ocr_used": False,
            "characters_extracted": 0,
            "chunks_created": 0,
            "average_chunk_size": 0,
            "embeddings_generated": 0,
            "faiss_indexed": 0,
            "bm25_indexed": 0,
            "retriever_test": "SKIPPED",
            "context_length": 0,
            "retrieved_chunks": 0,
            "status": "FAILED",
            "reason": None,
        }

        try:
            async with uow:
                job = await uow.processing_job_repository.get_by_id(job_id)
                if not job:
                    return

                report["status"] = job.status.value
                report["reason"] = job.error_message

                # Get extraction data
                content = await uow.document_content_repository.get_by_document_id(document_id)
                if content:
                    report["characters_extracted"] = content.character_count or 0
                    metadata = content.content_metadata or {}
                    report["ocr_used"] = metadata.get("ocr_used", False)

                # Get chunks data
                chunks = await uow.document_chunk_repository.list_by_document(document_id)
                report["chunks_created"] = len(chunks)
                if chunks:
                    total_chars = sum(len(c.text) for c in chunks)
                    report["average_chunk_size"] = total_chars // len(chunks)

                    indexed_chunks = [c for c in chunks if c.vector_id]
                    report["embeddings_generated"] = len(indexed_chunks)
                    report["faiss_indexed"] = len(indexed_chunks)

                    # BM25 is usually in sync if FAISS succeeded and keyword service is present
                    if self._keyword_index_service:
                        report["bm25_indexed"] = len(indexed_chunks)

                # Perform retriever test if COMPLETED
                if job.status.value == "COMPLETED" and chunks:
                    try:
                        query = "What is this document about?"
                        query_embedding = await self._embedding_service.generate_embeddings([query])
                        if query_embedding and len(query_embedding) > 0:
                            semantic_results = await self._vector_index_service.search(
                                query_embedding[0], top_k=5
                            )

                            # Filter results for this document
                            doc_chunks = [
                                r
                                for r in semantic_results
                                if r.vector_id in [c.vector_id for c in chunks]
                            ]

                            report["retrieved_chunks"] = len(doc_chunks)
                            report["context_length"] = sum(
                                len(c.text)
                                for c in chunks
                                if c.vector_id in [r.vector_id for r in doc_chunks]
                            )
                            report["retriever_test"] = "PASS" if len(doc_chunks) > 0 else "FAIL"
                    except Exception:
                        pass
                        report["retriever_test"] = "ERROR"

                job.ingestion_report = report
                await uow.processing_job_repository.update(job)
                await uow.commit()

                pass

        except Exception:
            pass

    async def extract_document(self, document_id: UUID) -> None:
        """Extract text from a document (idempotent).

        Args:
            document_id: The UUID of the document to extract.

        Raises:
            DocumentProcessingException: If extraction fails.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                # Check if extraction already exists
                existing_content = await uow.document_content_repository.get_by_document_id(
                    document_id
                )
                if existing_content and existing_content.raw_text:
                    pass
                    return

                # Load the document
                document = await uow.document_repository.get_by_id(document_id)
                if document is None:
                    raise DocumentProcessingException(f"Document not found: {document_id}")

                pass

                from pathlib import Path

                from app.core.config import get_settings

                settings = get_settings()
                absolute_file_path = str(Path(settings.STORAGE_PATH) / document.storage_path)

                # Extract text
                extraction_result = await self._extraction_service.extract(
                    file_path=absolute_file_path,
                    file_type=document.file_type.value,
                )

                # Store DocumentContent
                await self._store_document_content(document_id, extraction_result, uow)

                await uow.commit()

                pass
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Extraction failed: {e}")

    async def summarize_document(self, document_id: UUID) -> None:
        """Generate and store a summary for a document (idempotent).

        Args:
            document_id: The UUID of the document to summarize.

        Raises:
            DocumentProcessingException: If summarization fails.
        """
        if not self._llm_provider:
            pass
            return

        uow = self._uow_factory()
        time.time()

        try:
            async with uow:
                # Check if summary already exists
                existing_content = await uow.document_content_repository.get_by_document_id(
                    document_id
                )
                if existing_content and existing_content.summary:
                    pass
                    return

                # Load document content
                content = await uow.document_content_repository.get_by_document_id(document_id)
                if content is None or not content.raw_text:
                    raise DocumentProcessingException(
                        f"Document content not found for: {document_id}"
                    )

                pass

                # Generate summary
                summary = await self._llm_provider.generate_summary(content.raw_text)

                # Store summary
                await uow.document_content_repository.update_summary(document_id, summary)

                await uow.commit()

                pass
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Summarization failed: {e}")

    async def chunk_document(self, document_id: UUID) -> list:
        """Chunk document text (idempotent).

        Args:
            document_id: The UUID of the document to chunk.

        Returns:
            List of chunk objects.

        Raises:
            DocumentProcessingException: If chunking fails.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                # Check if chunks already exist
                existing_chunks = await uow.document_chunk_repository.list_by_document(document_id)
                if existing_chunks:
                    pass
                    # Return existing chunks for downstream stages
                    return self._convert_chunks_to_objects(existing_chunks)

                # Load document content
                content = await uow.document_content_repository.get_by_document_id(document_id)
                if content is None or not content.raw_text:
                    raise DocumentProcessingException(
                        f"Document content not found for: {document_id}"
                    )

                pass

                # Chunk text
                chunks = self._chunking_service.chunk(
                    text=content.raw_text,
                    pages=(
                        content.content_metadata.get("pages", [])
                        if content.content_metadata
                        else []
                    ),
                )

                # Store chunks (without vector_ids initially)
                await self._store_document_chunks(document_id, chunks, vector_ids=None, uow=uow)

                await uow.commit()

                pass

                return chunks
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Chunking failed: {e}")

    async def generate_embeddings(self, document_id: UUID, chunks: list) -> list:
        """Generate embeddings for document chunks (idempotent).

        Args:
            document_id: The UUID of the document.
            chunks: List of chunk objects.

        Returns:
            List of embedding vectors.

        Raises:
            DocumentProcessingException: If embedding generation fails.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                pass

                # Generate embeddings
                chunk_texts = [chunk.text for chunk in chunks]
                embeddings = await self._embedding_service.generate_embeddings(chunk_texts)

                # Verify parity
                if len(embeddings) != len(chunks):
                    raise DocumentProcessingException(
                        f"Embedding count mismatch: generated {len(embeddings)} for {len(chunks)} chunks"
                    )

                # Assign vector_ids to chunks
                vector_ids = [str(uuid4()) for _ in chunks]
                await self._update_chunk_vector_ids(document_id, vector_ids, uow)

                await uow.commit()

                pass

                return embeddings
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Embedding generation failed: {e}")

    async def index_vectors(self, document_id: UUID, chunks: list, embeddings: list) -> None:
        """Index vectors for search (idempotent).

        Args:
            document_id: The UUID of the document.
            chunks: List of chunk objects (not used directly, loaded from DB).
            embeddings: List of embedding vectors.

        Raises:
            DocumentProcessingException: If indexing fails.
        """
        uow = self._uow_factory()
        try:
            async with uow:
                # Get chunks with vector_ids from database
                existing_chunks = await uow.document_chunk_repository.list_by_document(document_id)
                if not existing_chunks:
                    raise DocumentProcessingException(
                        f"No chunks found for document: {document_id}"
                    )

                # Check if vectors already indexed
                vector_ids = [chunk.vector_id for chunk in existing_chunks if chunk.vector_id]
                if not vector_ids:
                    raise DocumentProcessingException(
                        f"No vector_ids found for document: {document_id}"
                    )

                # Verify vector_ids and embeddings match
                if len(vector_ids) != len(embeddings):
                    raise DocumentProcessingException(
                        f"Vector count mismatch: {len(vector_ids)} vector_ids vs {len(embeddings)} embeddings"
                    )

                pass

                # Index vectors
                await self._vector_index_service.index_vectors(vector_ids, embeddings)

                await uow.commit()

                pass
        except DocumentProcessingException:
            raise
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Vector indexing failed: {e}")

    async def index_chunks(self, document_id: UUID, chunks: list) -> None:
        """Index chunks for keyword search (idempotent).

        Args:
            document_id: The UUID of the document.
            chunks: List of chunk objects.

        Raises:
            DocumentProcessingException: If indexing fails.
        """
        if not self._keyword_index_service:
            pass
            return

        uow = self._uow_factory()
        try:
            async with uow:
                # Get chunks with IDs
                existing_chunks = await uow.document_chunk_repository.list_by_document(document_id)
                if not existing_chunks:
                    pass
                    return

                pass

                # Prepare chunks for keyword indexing
                keyword_chunks = [
                    (chunk.vector_id, chunk.text, chunk.chunk_metadata) for chunk in existing_chunks
                ]

                # Index chunks (persistence handled by KeywordIndexService)
                self._keyword_index_service.index_chunks(keyword_chunks)

                pass
        except Exception as e:
            pass
            raise DocumentProcessingException(f"Keyword indexing failed: {e}")

    async def _store_document_content(
        self, document_id: UUID, extraction_result, uow: IUnitOfWork
    ) -> None:
        """Store or update document content.

        Args:
            document_id: The document UUID.
            extraction_result: The extraction result from ExtractionService.
            uow: UnitOfWork instance.
        """
        existing_content = await uow.document_content_repository.get_by_document_id(document_id)

        # Calculate Document Profile metadata
        metadata = extraction_result.metadata or {}
        metadata["ocr_used"] = getattr(extraction_result, "ocr_used", False)

        # 1. Estimated reading time (assuming 200 WPM, ~1000 chars per min)
        char_count = extraction_result.character_count or 0
        metadata["estimated_reading_time_minutes"] = max(1, char_count // 1000)

        # 2. Number of pages
        metadata["page_count"] = extraction_result.page_count or 1

        # 3. Simple heuristics for document type based on keywords
        raw_lower = extraction_result.raw_text[:2000].lower() if extraction_result.raw_text else ""
        if "resume" in raw_lower or "experience" in raw_lower and "education" in raw_lower:
            doc_type = "Resume"
        elif "patient" in raw_lower and ("diagnosis" in raw_lower or "clinic" in raw_lower):
            doc_type = "Medical Report"
        elif "abstract" in raw_lower and "methodology" in raw_lower:
            doc_type = "Research Paper"
        elif "invoice" in raw_lower and "total" in raw_lower:
            doc_type = "Invoice"
        else:
            doc_type = "General Document"

        metadata["type"] = doc_type

        if existing_content:
            # Update existing content
            existing_content.raw_text = extraction_result.raw_text
            existing_content.page_count = extraction_result.page_count
            existing_content.character_count = extraction_result.character_count
            existing_content.content_metadata = metadata
            existing_content.language = None  # Language detection not implemented yet
            await uow.document_content_repository.update(existing_content)
        else:
            # Create new content
            content = DocumentContent(
                document_id=str(document_id),
                raw_text=extraction_result.raw_text,
                page_count=extraction_result.page_count,
                character_count=extraction_result.character_count,
                content_metadata=metadata,
                language=None,  # Language detection not implemented yet
            )
            await uow.document_content_repository.create(content)

    async def _store_document_chunks(
        self,
        document_id: UUID,
        chunks,
        vector_ids: list[str] | None,
        uow: IUnitOfWork,
    ) -> None:
        """Store document chunks with optional vector IDs.

        Args:
            document_id: The document UUID.
            chunks: List of chunk objects from ChunkingService.
            vector_ids: Optional list of vector IDs for the chunks.
            uow: UnitOfWork instance.
        """
        # Delete existing chunks for this document (if regenerating)
        await uow.document_chunk_repository.delete_by_document(document_id)

        # Create DocumentChunk records
        for i, chunk in enumerate(chunks):
            vector_id = vector_ids[i] if vector_ids else None
            document_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                page_number=chunk.page_number,
                start_character=chunk.start_character,
                end_character=chunk.end_character,
                vector_id=vector_id,
                chunk_metadata=chunk.metadata,
            )
            await uow.document_chunk_repository.create(document_chunk)

    async def _update_chunk_vector_ids(
        self, document_id: UUID, vector_ids: list[str], uow: IUnitOfWork
    ) -> None:
        """Update vector IDs for document chunks.

        Args:
            document_id: The document UUID.
            vector_ids: List of vector IDs.
            uow: UnitOfWork instance.
        """
        chunks = await uow.document_chunk_repository.list_by_document(document_id)
        for chunk, vector_id in zip(chunks, vector_ids, strict=False):
            chunk.vector_id = vector_id

    def _convert_chunks_to_objects(self, chunks: list[DocumentChunk]) -> list:
        """Convert DocumentChunk entities to chunk objects.

        Args:
            chunks: List of DocumentChunk entities.

        Returns:
            List of chunk-like objects.
        """

        # Simple conversion - in production you might have a proper chunk class
        class ChunkObject:
            def __init__(self, chunk: DocumentChunk):
                self.chunk_index = chunk.chunk_index
                self.text = chunk.text
                self.page_number = chunk.page_number
                self.start_character = chunk.start_character
                self.end_character = chunk.end_character
                self.metadata = chunk.chunk_metadata

        return [ChunkObject(chunk) for chunk in chunks]

    async def _load_existing_embeddings(
        self, document_id: UUID, chunks: list[DocumentChunk]
    ) -> list:
        """Load existing embeddings from vector store.

        Args:
            document_id: The document UUID.
            chunks: List of DocumentChunk entities.

        Returns:
            List of embedding vectors.
        """
        # In production, you would load these from the vector store
        # For now, return empty list as this requires vector store query capability
        pass
        return []
