"""SQLAlchemy implementation of ChatMessage repository."""

import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.chat_message import ChatMessageRepository

logger = logging.getLogger(__name__)


class SQLAlchemyChatMessageRepository(ChatMessageRepository):
    """SQLAlchemy implementation of ChatMessage repository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session.

        Args:
            session: SQLAlchemy async session.
        """
        self._session = session

    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message record.

        Args:
            message: The ChatMessage entity to create.

        Returns:
            The created ChatMessage entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(message)
            await self._session.flush()
            await self._session.refresh(message)
            pass
            return message
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create", f"Failed to create chat message: {e}")

    async def get_by_id(self, message_id: UUID) -> ChatMessage | None:
        """Retrieve a chat message by its unique identifier.

        Args:
            message_id: The UUID of the chat message to retrieve.

        Returns:
            The ChatMessage entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ChatMessage).where(ChatMessage.id == message_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_by_id", f"Failed to retrieve chat message: {e}")

    async def list_by_session(
        self, session_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """Retrieve chat messages by session ID.

        Args:
            session_id: The UUID of the session.
            offset: Number of messages to skip.
            limit: Maximum number of messages to return.

        Returns:
            List of ChatMessage entities ordered by created_at ascending.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "list_by_session", f"Failed to retrieve chat messages: {e}"
            )

    async def delete_by_session(self, session_id: UUID) -> None:
        """Delete all messages for a session.

        Args:
            session_id: The UUID of the session.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        try:
            await self._session.execute(
                delete(ChatMessage).where(ChatMessage.session_id == session_id)
            )
            await self._session.flush()
            pass
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "delete_by_session", f"Failed to delete chat messages: {e}"
            )

    async def delete(self, message_id: UUID) -> None:
        """Delete a chat message by its unique identifier.

        Args:
            message_id: The UUID of the chat message to delete.

        Raises:
            EntityNotFoundException: If the message is not found.
            DatabaseOperationException: If the deletion fails.
        """
        try:
            message = await self.get_by_id(message_id)
            if message is None:
                raise EntityNotFoundException("ChatMessage", str(message_id))

            await self._session.delete(message)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete", f"Failed to delete chat message: {e}")
