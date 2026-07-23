"""Interface for ChatSession repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.chat_session import ChatSession


class ChatSessionRepository(ABC):
    """Abstract interface for ChatSession repository operations.

    This interface defines the contract for ChatSession data access operations.
    Implementations can use different backends (SQLAlchemy, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, session: ChatSession) -> ChatSession:
        """Create a new chat session record.

        Args:
            session: The ChatSession entity to create.

        Returns:
            The created ChatSession entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        pass

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> ChatSession | None:
        """Retrieve a chat session by its unique identifier.

        Args:
            session_id: The UUID of the chat session to retrieve.

        Returns:
            The ChatSession entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update(self, session: ChatSession) -> ChatSession:
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        """Delete a chat session by its unique identifier.

        Args:
            session_id: The UUID of the chat session to delete.

        Raises:
            EntityNotFoundException: If the session is not found.
            DatabaseOperationException: If the deletion fails.
        """
        pass

    @abstractmethod
    async def exists(self, session_id: UUID) -> bool:
        """Check if a chat session exists.

        Args:
            session_id: The UUID of the chat session to check.

        Returns:
            True if the session exists, False otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
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
        pass
