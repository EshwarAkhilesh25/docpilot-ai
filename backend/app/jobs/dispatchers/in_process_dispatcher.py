"""In-process job dispatcher implementation."""

import asyncio
import logging
from uuid import UUID

from app.chunking.strategies.recursive_text_chunk_strategy import RecursiveTextChunkStrategy
from app.db.unit_of_work import UnitOfWorkFactory
from app.embeddings.interfaces.embedding_provider import EmbeddingProvider
from app.ingestion.interfaces.transcription_provider import TranscriptionProvider
from app.ingestion.pipeline.ingestion_pipeline import IngestionPipeline
from app.jobs.exceptions import JobDispatchException
from app.jobs.interfaces.job_dispatcher import JobDispatcher
from app.jobs.workers.document_processing_worker import DocumentProcessingWorker
from app.keyword_search.interfaces.keyword_index_provider import KeywordIndexProvider
from app.keyword_search.services.keyword_index_service import KeywordIndexService
from app.services.chunking_service import ChunkingService
from app.services.document_processing_service import DocumentProcessingServiceImpl
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService
from app.services.vector_index_service import VectorIndexService
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider

logger = logging.getLogger(__name__)


class InProcessJobDispatcher(JobDispatcher):
    """In-process job dispatcher using asyncio.create_task().

    This dispatcher schedules jobs to run in the background using asyncio tasks.
    It does not block the request thread and returns immediately after scheduling.

    This implementation is suitable for development and testing. For production,
    consider using Celery, Dramatiq, or RQ for distributed job processing.
    """

    def __init__(
        self,
        ingestion_pipeline: IngestionPipeline,
        embedding_provider: EmbeddingProvider,
        vector_index_path: str | None = None,
        transcription_provider: TranscriptionProvider | None = None,
        keyword_index_provider: KeywordIndexProvider | None = None,
    ):
        """Initialize the in-process job dispatcher.

        Args:
            ingestion_pipeline: Ingestion pipeline for document processing.
            embedding_provider: Embedding provider for generating chunk embeddings.
            vector_index_path: Optional path for persisting the vector index.
            transcription_provider: Optional transcription provider for audio files.
            keyword_index_provider: Optional keyword index provider for BM25 search.
        """
        # Create specialized services for each processing stage
        extraction_service = ExtractionService(ingestion_pipeline)

        chunking_service = ChunkingService(
            chunk_strategy=RecursiveTextChunkStrategy(
                chunk_size=1000,
                chunk_overlap=200,
            )
        )

        embedding_service = EmbeddingService(embedding_provider)

        vector_provider = FAISSVectorProvider(
            index_path=vector_index_path,
            embedding_model="BAAI/bge-small-en-v1.5",
        )
        vector_index_service = VectorIndexService(
            vector_provider=vector_provider,
            index_path=vector_index_path,
            embedding_model="BAAI/bge-small-en-v1.5",
        )

        # Create keyword index service if provider is available
        keyword_index_service = None
        if keyword_index_provider:
            keyword_index_service = KeywordIndexService(keyword_index_provider)

        # Create the processing service with all dependencies
        processing_service = DocumentProcessingServiceImpl(
            uow_factory=UnitOfWorkFactory.create,
            extraction_service=extraction_service,
            chunking_service=chunking_service,
            embedding_service=embedding_service,
            vector_index_service=vector_index_service,
            keyword_index_service=keyword_index_service,
            llm_provider=None,  # Will be injected separately if configured
        )

        # Create the worker with the processing service
        self._worker = DocumentProcessingWorker(
            uow_factory=UnitOfWorkFactory.create,
            processing_service=processing_service,
        )

    async def enqueue_document_processing(self, document_id: UUID) -> None:
        """Enqueue a document processing job.

        Schedules the job to run in the background using asyncio.create_task().
        Returns immediately without blocking.

        Args:
            document_id: The UUID of the document to process.

        Raises:
            JobDispatchException: If the job cannot be enqueued.
        """
        try:
            # Schedule the job to run in the background
            asyncio.create_task(self._worker.process(document_id))
            pass
        except Exception as e:
            pass
            raise JobDispatchException(f"Failed to enqueue job: {e}")

    async def enqueue_document_deletion(self, document_id: UUID) -> None:
        """Enqueue a document deletion job.

        Args:
            document_id: The UUID of the document to delete.

        Raises:
            JobDispatchException: If the job cannot be enqueued.
        """
        try:
            # TODO: Implement document deletion worker
            pass
        except Exception as e:
            pass
            raise JobDispatchException(f"Failed to enqueue job: {e}")
