"""SQLAlchemy implementation of Document repository."""

import logging
from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.enums import ProcessingStatus
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.document import DocumentRepository

logger = logging.getLogger(__name__)


class SQLAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy implementation of Document repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        self._session = session

    async def create(self, document: Document) -> Document:
        """Create a new document in the database.

        Args:
            document: The Document entity to create.

        Returns:
            The created Document entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(document)
            await self._session.flush()
            await self._session.refresh(document)
            pass
            return document
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create", str(e))

    async def get_by_id(self, document_id: UUID) -> Document | None:
        """Retrieve a document by its unique identifier.

        Args:
            document_id: The UUID of the document to retrieve.

        Returns:
            The Document entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(select(Document).where(Document.id == document_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document", str(e))

    async def list_by_user(self, user_id: UUID, offset: int = 0, limit: int = 20) -> list[Document]:
        """List documents belonging to a specific user with pagination.

        Args:
            user_id: The UUID of the user whose documents to list.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of Document entities belonging to the user.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(Document)
                .where(Document.user_id == user_id)
                .order_by(Document.uploaded_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("list_documents", str(e))

    async def update(self, document: Document) -> Document:
        """Update an existing document in the database.

        Args:
            document: The Document entity with updated fields.

        Returns:
            The updated Document entity.

        Raises:
            DatabaseOperationException: If the update fails.
            EntityNotFoundException: If the document does not exist.
        """
        try:
            existing = await self.get_by_id(document.id)
            if existing is None:
                raise EntityNotFoundException("Document", str(document.id))

            merged = await self._session.merge(document)
            await self._session.flush()
            await self._session.refresh(merged)
            pass
            return merged
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_document", str(e))

    async def delete(self, document_id: UUID) -> None:
        """Delete a document by its unique identifier.

        Args:
            document_id: The UUID of the document to delete.

        Raises:
            DatabaseOperationException: If the deletion fails.
            EntityNotFoundException: If the document does not exist.
        """
        try:
            document = await self.get_by_id(document_id)
            if document is None:
                raise EntityNotFoundException("Document", str(document_id))

            await self._session.delete(document)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete_document", str(e))

    async def exists(self, document_id: UUID) -> bool:
        """Check if a document exists.

        Args:
            document_id: The UUID of the document to check.

        Returns:
            True if the document exists, False otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(func.count()).where(Document.id == document_id)
            )
            count = result.scalar() or 0
            return count > 0
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("check_document_existence", str(e))

    async def count_by_user(self, user_id: UUID) -> int:
        """Count documents belonging to a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The number of documents belonging to the user.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(func.count()).where(Document.user_id == user_id)
            )
            return result.scalar() or 0
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("count_documents", str(e))

    async def search_by_filename(
        self, user_id: UUID, search_term: str, offset: int = 0, limit: int = 20
    ) -> list[Document]:
        """Search documents by filename for a specific user.

        Args:
            user_id: The UUID of the user.
            search_term: The search term to match in filenames.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of matching Document entities.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(Document)
                .where(
                    Document.user_id == user_id,
                    Document.original_filename.ilike(f"%{search_term}%"),
                )
                .order_by(Document.uploaded_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("search_documents", str(e))

    async def list_by_status(
        self, user_id: UUID, status: ProcessingStatus, offset: int = 0, limit: int = 20
    ) -> list[Document]:
        """List documents by processing status for a specific user.

        Args:
            user_id: The UUID of the user.
            status: The processing status to filter by.
            offset: The number of documents to skip (for pagination).
            limit: The maximum number of documents to return.

        Returns:
            A list of Document entities with the specified status.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(Document)
                .where(
                    Document.user_id == user_id,
                    cast(Document.processing_status, String) == status.value,
                )
                .order_by(Document.uploaded_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("list_documents_by_status", str(e))

    async def get_storage_path(self, document_id: UUID) -> str | None:
        """Get the storage path for a document.

        Args:
            document_id: The UUID of the document.

        Returns:
            The storage path if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(Document.storage_path).where(Document.id == document_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_storage_path", str(e))
