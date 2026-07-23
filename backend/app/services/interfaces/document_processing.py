"""Interface for document processing service."""

from abc import ABC, abstractmethod
from uuid import UUID


class DocumentProcessingService(ABC):
    """Abstract interface for document processing service.

    This service handles the business logic for processing documents,
    including loading the document, invoking the ingestion pipeline,
    and handling extraction results.

    The worker delegates all document-specific logic to this service.
    """

    @abstractmethod
    async def process(self, document_id: UUID) -> None:
        """Process a document.

        This method loads the document, invokes the ingestion pipeline,
        and handles the extraction result.

        Args:
            document_id: The UUID of the document to process.

        Raises:
            DocumentProcessingException: If processing fails.
        """
        pass

    @abstractmethod
    async def generate_ingestion_report(self, document_id: UUID, job_id: UUID) -> None:
        pass

    @abstractmethod
    async def extract_document(self, document_id: UUID) -> None:
        pass

    @abstractmethod
    async def summarize_document(self, document_id: UUID) -> None:
        pass

    @abstractmethod
    async def chunk_document(self, document_id: UUID) -> list:
        pass

    @abstractmethod
    async def generate_embeddings(self, document_id: UUID, chunks: list) -> list:
        pass

    @abstractmethod
    async def index_vectors(self, document_id: UUID, chunks: list, embeddings: list) -> None:
        pass

    @abstractmethod
    async def index_chunks(self, document_id: UUID, chunks: list) -> None:
        pass
