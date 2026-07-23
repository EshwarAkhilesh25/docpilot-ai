"""Interface for ChatMessage repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.chat_message import ChatMessage


class ChatMessageRepository(ABC):
    """Abstract interface for ChatMessage repository operations.

    This interface defines the contract for ChatMessage data access operations.
    Implementations can use different backends (SQLAlchemy, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message record.

        Args:
            message: The ChatMessage entity to create.

        Returns:
            The created ChatMessage entity with generated fields populated.

        Raises:
            DatabaseOperationException: If the creation fails.
        """
        pass

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> ChatMessage | None:
        """Retrieve a chat message by its unique identifier.

        Args:
            message_id: The UUID of the chat message to retrieve.

        Returns:
            The ChatMessage entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete_by_session(self, session_id: UUID) -> None:
        """Delete all messages for a session.

        Args:
            session_id: The UUID of the session.

        Raises:
            DatabaseOperationException: If the deletion fails.
        """
        pass

    @abstractmethod
    async def delete(self, message_id: UUID) -> None:
        """Delete a chat message by its unique identifier.

        Args:
            message_id: The UUID of the chat message to delete.

        Raises:
            EntityNotFoundException: If the message is not found.
            DatabaseOperationException: If the deletion fails.
        """
        pass
