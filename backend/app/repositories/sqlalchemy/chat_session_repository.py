"""SQLAlchemy implementation of ChatSession repository."""

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.repositories.exceptions import DatabaseOperationException, EntityNotFoundException
from app.repositories.interfaces.chat_session import ChatSessionRepository

logger = logging.getLogger(__name__)


class SQLAlchemyChatSessionRepository(ChatSessionRepository):
    """SQLAlchemy implementation of ChatSession repository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session.

        Args:
            session: SQLAlchemy async session.
        """
        self._session = session

    async def create(self, session: ChatSession) -> ChatSession:
        """Create a new chat session record.

        Args:
            session: The ChatSession entity to create.

        Returns:
            The created ChatSession entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        try:
            self._session.add(session)
            await self._session.flush()
            await self._session.refresh(session)
            pass
            return session
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create", f"Failed to create chat session: {e}")

    async def get_by_id(self, session_id: UUID) -> ChatSession | None:
        """Retrieve a chat session by its unique identifier.

        Args:
            session_id: The UUID of the chat session to retrieve.

        Returns:
            The ChatSession entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ChatSession).where(ChatSession.id == session_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_by_id", f"Failed to retrieve chat session: {e}")

    async def list_by_user(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[ChatSession]:
        """Retrieve chat sessions by user ID.

        Args:
            user_id: The UUID of the user.
            offset: Number of sessions to skip.
            limit: Maximum number of sessions to return.

        Returns:
            List of ChatSession entities ordered by created_at descending.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "list_by_user", f"Failed to retrieve chat sessions: {e}"
            )

    async def delete(self, session_id: UUID) -> None:
        """Delete a chat session by its unique identifier.

        Args:
            session_id: The UUID of the chat session to delete.

        Raises:
            EntityNotFoundException: If the session is not found.
            DatabaseOperationException: If the deletion fails.
        """
        try:
            session = await self.get_by_id(session_id)
            if session is None:
                raise EntityNotFoundException("ChatSession", str(session_id))

            await self._session.delete(session)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete", f"Failed to delete chat session: {e}")

    async def exists(self, session_id: UUID) -> bool:
        """Check if a chat session exists.

        Args:
            session_id: The UUID of the chat session to check.

        Returns:
            True if the session exists, False otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            result = await self._session.execute(
                select(ChatSession.id).where(ChatSession.id == session_id)
            )
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "exists", f"Failed to check chat session existence: {e}"
            )

    async def list_with_message_info(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[dict]:
        """Retrieve chat sessions with message count and last message preview.

        This method optimizes listing by avoiding N+1 queries. It returns
        sessions with message metadata in a single database query.

        Args:
            user_id: The UUID of the user.
            offset: Number of sessions to skip.
            limit: Maximum number of sessions to return.

        Returns:
            List of dictionaries with:
            - session: ChatSession entity
            - message_count: int
            - last_message_preview: str (truncated to 100 chars)

        Raises:
            DatabaseOperationException: If the query fails.
        """
        try:
            # Subquery to get message count and last message for each session
            message_subquery = (
                select(
                    ChatMessage.session_id,
                    func.count(ChatMessage.id).label("message_count"),
                    func.max(ChatMessage.content).label("last_message_content"),
                )
                .group_by(ChatMessage.session_id)
                .subquery()
            )

            # Main query joining sessions with message info
            result = await self._session.execute(
                select(
                    ChatSession,
                    message_subquery.c.message_count,
                    message_subquery.c.last_message_content,
                )
                .outerjoin(message_subquery, ChatSession.id == message_subquery.c.session_id)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
                .offset(offset)
                .limit(limit)
            )

            rows = result.all()

            # Build result list with truncated previews
            conversations = []
            for session, message_count, last_message_content in rows:
                # Truncate preview to 100 characters
                preview = ""
                if last_message_content:
                    preview = last_message_content[:100]
                    if len(last_message_content) > 100:
                        preview += "..."

                conversations.append(
                    {
                        "session": session,
                        "message_count": message_count or 0,
                        "last_message_preview": preview,
                    }
                )

            return conversations

        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException(
                "list_with_message_info", f"Failed to retrieve chat sessions with message info: {e}"
            )

    async def update(self, session: ChatSession) -> ChatSession:
        self._session.add(session)
        await self._session.flush()
        return session
