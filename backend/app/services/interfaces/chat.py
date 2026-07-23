from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.chat import ChatRequest, ChatResponse


class ChatService(ABC):
    """Abstract service interface for chat-related business operations.

    This interface defines the contract for chat business logic operations.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
    async def send_message(self, request: ChatRequest, user_id: UUID) -> ChatResponse:
        """Send a chat message and get an AI response.

        Args:
            request: The chat request containing message and optional document context.
            user_id: The UUID of the user sending the message.

        Returns:
            ChatResponse containing the AI's response and session information.

        Raises:
            ValidationError: If the request is invalid.
            NotFoundError: If specified documents do not exist or user lacks access.
        """

    @abstractmethod
    async def get_chat_history(self, session_id: UUID, user_id: UUID) -> list[dict]:
        """Retrieve the message history for a chat session.

        Args:
            session_id: The UUID of the chat session.
            user_id: The UUID of the user requesting the history.

        Returns:
            A list of message dictionaries in chronological order.

        Raises:
            NotFoundError: If the session does not exist or user lacks access.
        """

    @abstractmethod
    async def list_chat_sessions(self, user_id: UUID, page: int = 1, page_size: int = 20) -> dict:
        """List chat sessions for a specific user with pagination.

        Args:
            user_id: The UUID of the user whose sessions to list.
            page: The page number (1-indexed).
            page_size: The number of items per page.

        Returns:
            A dictionary containing paginated session information.

        Raises:
            ValidationError: If pagination parameters are invalid.
        """

    @abstractmethod
    async def delete_chat_session(self, session_id: UUID, user_id: UUID) -> None:
        """Delete a chat session for a specific user.

        Args:
            session_id: The UUID of the chat session to delete.
            user_id: The UUID of the user requesting deletion.

        Raises:
            NotFoundError: If the session does not exist or user lacks access.
        """
