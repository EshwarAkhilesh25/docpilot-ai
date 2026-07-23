"""SQLAlchemy implementation of DocumentChunk repository."""

import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.document_chunk import DocumentChunkRepository

logger = logging.getLogger(__name__)


class SQLAlchemyDocumentChunkRepository(DocumentChunkRepository):
    """SQLAlchemy implementation of DocumentChunk repository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session.

        Args:
            session: SQLAlchemy async session.
        """
        self._session = session

    async def create(self, chunk: DocumentChunk) -> DocumentChunk:
        """Create a new document chunk record.

        Args:
            chunk: The DocumentChunk entity to create.

        Returns:
            The created DocumentChunk entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(chunk)
            await self._session.flush()
            await self._session.refresh(chunk)
            pass
            return chunk
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create_document_chunk", str(e))

    async def get_by_id(self, chunk_id: UUID) -> DocumentChunk | None:
        """Retrieve a document chunk by its unique identifier.

        Args:
            chunk_id: The UUID of the document chunk to retrieve.

        Returns:
            The DocumentChunk entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_chunk", str(e))

    async def list_by_document(
        self, document_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[DocumentChunk]:
        """Retrieve document chunks by document ID.

        Args:
            document_id: The UUID of the document.
            offset: Number of chunks to skip.
            limit: Maximum number of chunks to return.

        Returns:
            List of DocumentChunk entities ordered by chunk_index.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_chunks", str(e))

    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks for a document.

        Args:
            document_id: The UUID of the document.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        try:
            await self._session.execute(
                delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )
            await self._session.flush()
            pass
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete_document_chunks", str(e))

    async def get_by_vector_id(self, vector_id: str) -> DocumentChunk | None:
        """Retrieve a document chunk by its vector ID.

        Args:
            vector_id: The vector ID of the document chunk to retrieve.

        Returns:
            The DocumentChunk entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentChunk).where(DocumentChunk.vector_id == vector_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_chunk", str(e))

    async def get_by_vector_ids(self, vector_ids: list[str]) -> list[DocumentChunk]:
        """Retrieve document chunks by their vector IDs.

        Args:
            vector_ids: List of vector IDs to retrieve.

        Returns:
            List of DocumentChunk entities for the given vector IDs.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            if not vector_ids:
                return []

            result = await self._session.execute(
                select(DocumentChunk).where(DocumentChunk.vector_id.in_(vector_ids))
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_chunks", str(e))

    async def delete(self, chunk_id: UUID) -> None:
        """Delete a document chunk by its unique identifier.

        Args:
            chunk_id: The UUID of the document chunk to delete.

        Raises:
            EntityNotFoundException: If the chunk is not found.
            DatabaseOperationException: If the deletion fails.
        """
        try:
            chunk = await self.get_by_id(chunk_id)
            if chunk is None:
                raise EntityNotFoundException("DocumentChunk", str(chunk_id))

            await self._session.delete(chunk)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete_document_chunk", str(e))
