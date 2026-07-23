"""Document service implementation."""

import logging
import time
from collections.abc import Callable
from uuid import UUID

from app.keyword_search.interfaces.keyword_index_provider import KeywordIndexProvider
from app.models.enums import ProcessingStatus
from app.schemas.document import (
    DocumentDetailsResponse,
    DocumentListResponse,
    DocumentSummaryResponse,
)
from app.services.exceptions import DocumentServiceException
from app.services.interfaces.document import DocumentService
from app.storage.interfaces.storage_provider import StorageProvider
from app.vectorstore.interfaces.vector_index_provider import VectorIndexProvider

logger = logging.getLogger(__name__)


class DocumentServiceImpl(DocumentService):
    """Implementation of document service.

    This service handles document-related business logic including:
    - Retrieving documents with ownership validation
    - Listing documents with pagination and filtering
    - Coordinated deletion of documents and related data
    - Retrieving document summaries
    """

    def __init__(
        self,
        uow_factory: Callable,
        storage_provider: StorageProvider,
        vector_provider: VectorIndexProvider,
        keyword_index_provider: KeywordIndexProvider = None,  # type: ignore
    ):
        """Initialize the document service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            storage_provider: Storage provider for file operations.
            vector_provider: Vector provider for vector index operations.
            keyword_index_provider: Optional keyword index provider for BM25 operations.
        """
        self._uow_factory = uow_factory
        self._storage_provider = storage_provider
        self._vector_provider = vector_provider
        self._keyword_index_provider = keyword_index_provider

    async def get_document(self, document_id: UUID, user_id: UUID) -> DocumentDetailsResponse:
        """Retrieve a document by its ID for a specific user.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the document.

        Returns:
            DocumentDetailsResponse containing the document details.

        Raises:
            DocumentServiceException: If the document does not exist or user lacks access.
        """
        time.time()
        uow = self._uow_factory()

        try:
            async with uow:
                document = await uow.document_repository.get_by_id(document_id)

                if document is None:
                    pass
                    raise DocumentServiceException("Document not found")

                if document.user_id != user_id:
                    pass
                    raise DocumentServiceException("Access denied")

                # Get document content for additional details
                content = await uow.document_content_repository.get_by_document_id(document_id)
                page_count = content.page_count if content else None
                character_count = content.character_count if content else None

                # Get chunk count
                chunks = await uow.document_chunk_repository.list_by_document(document_id)
                chunk_count = len(chunks) if chunks else None

                # Get latest processing job for stage information
                jobs = await uow.processing_job_repository.list_by_document(
                    document_id, offset=0, limit=1
                )
                processing_stage = jobs[0].current_stage if jobs else None

                response = DocumentDetailsResponse(
                    id=document.id,
                    original_filename=document.original_filename,
                    file_type=document.file_type,
                    file_size=document.file_size,
                    processing_status=document.processing_status,
                    processing_stage=processing_stage,
                    uploaded_at=document.uploaded_at,
                    processed_at=document.processed_at,
                    page_count=page_count,
                    character_count=character_count,
                    chunk_count=chunk_count,
                )

                pass

                return response

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to retrieve document: {e}")

    async def list_documents(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: ProcessingStatus | None = None,
    ) -> DocumentListResponse:
        """List documents for a specific user with pagination and filtering.

        Args:
            user_id: The UUID of the user whose documents to list.
            page: The page number (1-indexed).
            page_size: The number of items per page.
            search: Optional search term for filename filtering.
            status: Optional processing status filter.

        Returns:
            DocumentListResponse containing paginated document summaries.

        Raises:
            DocumentServiceException: If pagination parameters are invalid or query fails.
        """
        time.time()

        # Validate pagination
        if page < 1:
            raise DocumentServiceException("Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise DocumentServiceException("Page size must be between 1 and 100")

        offset = (page - 1) * page_size
        uow = self._uow_factory()

        try:
            async with uow:
                # Get documents based on filters
                if search and status:
                    documents = await uow.document_repository.list_by_status(
                        user_id, status, offset=offset, limit=page_size
                    )
                    # Filter by search term (client-side for simplicity)
                    documents = [
                        d for d in documents if search.lower() in d.original_filename.lower()
                    ]
                elif search:
                    documents = await uow.document_repository.search_by_filename(
                        user_id, search, offset=offset, limit=page_size
                    )
                elif status:
                    documents = await uow.document_repository.list_by_status(
                        user_id, status, offset=offset, limit=page_size
                    )
                else:
                    documents = await uow.document_repository.list_by_user(
                        user_id, offset=offset, limit=page_size
                    )

                # Get total count
                total = await uow.document_repository.count_by_user(user_id)

                # Build response items
                items = [
                    DocumentSummaryResponse(
                        id=doc.id,
                        original_filename=doc.original_filename,
                        file_type=doc.file_type,
                        processing_status=doc.processing_status,
                        uploaded_at=doc.uploaded_at,
                    )
                    for doc in documents
                ]

                total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

                response = DocumentListResponse(
                    items=items,
                    total=total,
                    page=page,
                    page_size=page_size,
                    total_pages=total_pages,
                )

                pass

                return response

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to list documents: {e}")

    async def delete_document(self, document_id: UUID, user_id: UUID) -> None:
        """Delete a document for a specific user with coordinated cleanup.

        This method performs a coordinated deletion workflow:
        1. Verify ownership
        2. Delete FAISS vectors
        3. Delete BM25 keyword index entries
        4. Delete DocumentChunk records
        5. Delete DocumentContent
        6. Delete ProcessingJob records
        7. Delete Chat sessions/messages
        8. Delete original stored file
        9. Delete Document database record

        Storage cleanup happens after successful DB commit.
        If storage deletion fails, it is logged but does not roll back the transaction.

        Args:
            document_id: The UUID of the document to delete.
            user_id: The UUID of the user requesting deletion.

        Raises:
            DocumentServiceException: If the document does not exist or user lacks access.
        """
        time.time()
        uow = self._uow_factory()
        storage_path = None

        try:
            async with uow:
                # Verify ownership
                document = await uow.document_repository.get_by_id(document_id)
                if document is None:
                    pass
                    raise DocumentServiceException("Document not found")

                if document.user_id != user_id:
                    pass
                    raise DocumentServiceException("Access denied")

                storage_path = document.storage_path

                # Get vector IDs and chunk IDs before deleting chunks
                chunks = await uow.document_chunk_repository.list_by_document(document_id)
                vector_ids = [chunk.vector_id for chunk in chunks if chunk.vector_id]
                chunk_ids = [chunk.id for chunk in chunks]

                # Delete vectors from FAISS index
                if vector_ids:
                    try:
                        await self._vector_provider.delete_vectors(vector_ids)
                        pass
                    except Exception:
                        pass
                        # Continue with deletion even if vector deletion fails

                # Delete BM25 keyword index entries
                if chunk_ids and self._keyword_index_provider:
                    try:
                        self._keyword_index_provider.remove_chunks(chunk_ids)
                        # Save the updated index
                        from pathlib import Path

                        from app.core.config import get_settings

                        settings = get_settings()
                        index_path = Path(settings.BM25_INDEX_PATH) / "bm25_index.pkl"
                        if index_path.exists():
                            self._keyword_index_provider.save_index(str(index_path))
                        pass
                    except Exception:
                        pass
                        # Continue with deletion even if BM25 deletion fails

                # Delete DocumentChunk records
                await uow.document_chunk_repository.delete_by_document(document_id)

                # Delete DocumentContent
                await uow.document_content_repository.delete_by_document(document_id)

                # Delete ProcessingJob records
                jobs = await uow.processing_job_repository.list_by_document(document_id)
                for job in jobs:
                    await uow.processing_job_repository.delete(job.id)

                # Delete Chat sessions and messages belonging to the document
                # Note: This requires chat repositories to be available
                # For now, we'll log this as a TODO
                pass

                # Delete Document record
                await uow.document_repository.delete(document_id)

                await uow.commit()

                pass

            # Storage cleanup after successful DB commit
            if storage_path:
                try:
                    await self._storage_provider.delete(storage_path)
                    pass
                except Exception:
                    pass
                    # Do not raise - DB transaction already committed

            pass

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to delete document: {e}")

    async def get_document_summary(self, document_id: UUID, user_id: UUID) -> dict | None:  # type: ignore
        """Retrieve the AI-generated summary of a document.

        Args:
            document_id: The UUID of the document.
            user_id: The UUID of the user requesting the summary.

        Returns:
            A dictionary containing the document summary, or None if not available.

        Raises:
            DocumentServiceException: If the document does not exist or user lacks access.
        """
        time.time()
        uow = self._uow_factory()

        try:
            async with uow:
                document = await uow.document_repository.get_by_id(document_id)

                if document is None:
                    pass
                    raise DocumentServiceException("Document not found")

                if document.user_id != user_id:
                    pass
                    raise DocumentServiceException("Access denied")

                # Load document content to get the stored summary
                content = await uow.document_content_repository.get_by_document_id(document_id)

                # Return the stored summary if available
                if content and content.summary:
                    pass
                    return {"summary": content.summary}
                else:
                    pass
                    return None

        except DocumentServiceException:
            raise
        except Exception as e:
            pass
            raise DocumentServiceException(f"Failed to retrieve document summary: {e}")
