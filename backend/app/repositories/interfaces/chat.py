from abc import ABC, abstractmethod
from uuid import UUID

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class ChatRepository(ABC):
    """Abstract repository interface for Chat entity operations.

    This interface defines the contract for chat session and message data access operations.
    Implementations should handle database-specific details while adhering
    to this interface for consistency and testability.
    """

    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create a new chat session in the database.

        Args:
            session: The ChatSession entity to create.

        Returns:
            The created ChatSession entity with generated fields populated.

        Raises:
            DatabaseError: If the creation fails due to database issues.
        """

    @abstractmethod
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message in the database.

        Args:
            message: The ChatMessage entity to create.

        Returns:
            The created ChatMessage entity with generated fields populated.

        Raises:
            DatabaseError: If the creation fails due to database issues.
        """

    @abstractmethod
    async def get_session(self, session_id: UUID) -> ChatSession | None:
        """Retrieve a chat session by its unique identifier.

        Args:
            session_id: The UUID of the chat session to retrieve.

        Returns:
            The ChatSession entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def list_sessions(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[ChatSession]:
        """List chat sessions belonging to a specific user with pagination.

        Args:
            user_id: The UUID of the user whose sessions to list.
            offset: The number of sessions to skip (for pagination).
            limit: The maximum number of sessions to return.

        Returns:
            A list of ChatSession entities belonging to the user.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """
