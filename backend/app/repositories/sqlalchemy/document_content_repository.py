"""SQLAlchemy implementation of DocumentContent repository."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_content import DocumentContent
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.document_content import DocumentContentRepository

logger = logging.getLogger(__name__)


class SQLAlchemyDocumentContentRepository(DocumentContentRepository):
    """SQLAlchemy implementation of DocumentContent repository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session.

        Args:
            session: SQLAlchemy async session.
        """
        self._session = session

    async def create(self, content: DocumentContent) -> DocumentContent:
        """Create a new document content record.

        Args:
            content: The DocumentContent entity to create.

        Returns:
            The created DocumentContent entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(content)
            await self._session.flush()
            await self._session.refresh(content)
            pass
            return content
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create_document_content", str(e))

    async def get_by_id(self, content_id: UUID) -> DocumentContent | None:
        """Retrieve a document content by its unique identifier.

        Args:
            content_id: The UUID of the document content to retrieve.

        Returns:
            The DocumentContent entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentContent).where(DocumentContent.id == content_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_content", str(e))

    async def get_by_document_id(self, document_id: UUID) -> DocumentContent | None:
        """Retrieve document content by document ID.

        Args:
            document_id: The UUID of the document.

        Returns:
            The DocumentContent entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentContent).where(DocumentContent.document_id == str(document_id))
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("retrieve_document_content", str(e))

    async def update(self, content: DocumentContent) -> DocumentContent:
        """Update an existing document content record.

        Args:
            content: The DocumentContent entity with updated fields.

        Returns:
            The updated DocumentContent entity.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the update fails.
        """
        try:
            existing = await self.get_by_id(content.id)
            if existing is None:
                raise EntityNotFoundException("DocumentContent", str(content.id))

            merged = await self._session.merge(content)
            await self._session.flush()
            await self._session.refresh(merged)
            pass
            return merged
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_document_content", str(e))

    async def update_summary(self, document_id: UUID, summary: str) -> DocumentContent:
        """Update the summary field for a document content record.

        Args:
            document_id: The UUID of the document.
            summary: The summary text to set.

        Returns:
            The updated DocumentContent entity.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the update fails.
        """
        try:
            content = await self.get_by_document_id(document_id)
            if content is None:
                raise EntityNotFoundException("DocumentContent", f"for document {document_id}")

            content.summary = summary
            await self._session.flush()
            await self._session.refresh(content)
            pass
            return content
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update_summary", str(e))

    async def delete(self, content_id: UUID) -> None:
        """Delete a document content by its unique identifier.

        Args:
            content_id: The UUID of the document content to delete.

        Raises:
            EntityNotFoundException: If the content is not found.
            DatabaseOperationException: If the deletion fails.
        """
        try:
            content = await self.get_by_id(content_id)
            if content is None:
                raise EntityNotFoundException("DocumentContent", str(content_id))

            await self._session.delete(content)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete_document_content", str(e))

    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete document content by document ID.

        Args:
            document_id: The UUID of the document.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        try:
            result = await self._session.execute(
                select(DocumentContent).where(DocumentContent.document_id == str(document_id))
            )
            content = result.scalar_one_or_none()

            if content is not None:
                await self._session.delete(content)
                await self._session.flush()
                pass
            else:
                pass
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "delete_by_document", f"Failed to delete document content: {e}"
            )
