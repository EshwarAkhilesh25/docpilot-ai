"""Script to manually trigger document reprocessing for debugging."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.chunking.strategies.recursive_text_chunk_strategy import (
    RecursiveTextChunkStrategy,
)
from app.db.unit_of_work import UnitOfWorkFactory
from app.ingestion.factory.processor_factory import ProcessorFactory
from app.ingestion.pipeline.ingestion_pipeline import IngestionPipeline
from app.jobs.workers.document_processing_worker import DocumentProcessingWorker
from app.keyword_search.providers.bm25_provider import BM25Provider
from app.keyword_search.services.keyword_index_service import KeywordIndexService
from app.services.chunking_service import ChunkingService
from app.services.document_processing_service import DocumentProcessingServiceImpl
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService
from app.services.vector_index_service import VectorIndexService
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider
from app.core.config import get_settings

settings = get_settings()


async def main():
    """Trigger reprocessing for the failing document."""
    document_id = "4acabc13-1e81-4746-9e78-a4ef7585f14e"  # Interview.pdf

    print(f"Triggering reprocessing for document: {document_id}")

    # Create processor factory
    processor_factory = ProcessorFactory()

    # Create ingestion pipeline
    ingestion_pipeline = IngestionPipeline(
        processor_factory=processor_factory,
        text_normalizer=None,
    )

    # Create embedding provider (using the same model as in production)
    from app.embeddings.providers.sentence_transformer_provider import (
        SentenceTransformerEmbeddingProvider,
    )

    embedding_provider = SentenceTransformerEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Create keyword index provider
    keyword_index_provider = BM25Provider()

    # Create specialized services
    extraction_service = ExtractionService(ingestion_pipeline)
    chunking_service = ChunkingService(
        chunk_strategy=RecursiveTextChunkStrategy(
            chunk_size=1000,
            chunk_overlap=200,
        )
    )
    embedding_service = EmbeddingService(embedding_provider)

    vector_provider = FAISSVectorProvider(
        index_path=str(Path(settings.FAISS_INDEX_PATH) / "index.faiss"),
        embedding_model="BAAI/bge-small-en-v1.5",
    )
    vector_index_service = VectorIndexService(
        vector_provider=vector_provider,
        index_path=str(Path(settings.FAISS_INDEX_PATH)),
        embedding_model="BAAI/bge-small-en-v1.5",
    )

    keyword_index_service = KeywordIndexService(keyword_index_provider)

    # Create processing service
    processing_service = DocumentProcessingServiceImpl(
        uow_factory=UnitOfWorkFactory.create,
        extraction_service=extraction_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_index_service=vector_index_service,
        keyword_index_service=keyword_index_service,
        llm_provider=None,
    )

    # Create worker
    worker = DocumentProcessingWorker(
        uow_factory=UnitOfWorkFactory.create,
        processing_service=processing_service,
    )

    # Process the document
    try:
        await worker.process(document_id)
        print(f"Successfully processed document: {document_id}")
    except Exception as e:
        print(f"Failed to process document: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
