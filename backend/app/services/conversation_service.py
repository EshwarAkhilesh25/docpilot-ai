"""Service for conversation management."""

import logging
import time
from uuid import UUID

from app.repositories.interfaces.chat_message import ChatMessageRepository
from app.repositories.interfaces.chat_session import ChatSessionRepository
from app.services.exceptions import ConversationServiceException

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations.

    This service handles listing, retrieving, and deleting conversations
    with proper ownership validation.
    """

    def __init__(
        self,
        session_repository: ChatSessionRepository,
        message_repository: ChatMessageRepository,
    ):
        """Initialize the conversation service.

        Args:
            session_repository: ChatSession repository instance.
            message_repository: ChatMessage repository instance.
        """
        self._session_repository = session_repository
        self._message_repository = message_repository

    async def list_conversations(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[dict]:
        """List all conversations for a user.

        Args:
            user_id: The UUID of the user.
            offset: Number of conversations to skip.
            limit: Maximum number of conversations to return.

        Returns:
            List of conversation dictionaries with:
            - session_id: UUID
            - created_at: datetime
            - updated_at: datetime
            - message_count: int
            - last_message_preview: str

        Raises:
            ConversationServiceException: If listing fails.
        """
        time.time()

        try:
            # Get sessions with message info in a single optimized query
            session_data = await self._session_repository.list_with_message_info(
                user_id, offset=offset, limit=limit
            )

            # Build response from repository results
            conversations = []
            for data in session_data:
                session = data["session"]
                conversations.append(
                    {
                        "session_id": session.id,
                        "created_at": session.created_at,
                        "updated_at": session.updated_at,
                        "message_count": data["message_count"],
                        "last_message_preview": data["last_message_preview"],
                    }
                )

            pass

            return conversations

        except Exception as e:
            pass
            raise ConversationServiceException(f"Failed to list conversations: {e}")

    async def get_conversation(self, session_id: UUID, user_id: UUID) -> dict:
        """Get a conversation with its message history.

        Args:
            session_id: The UUID of the conversation session.
            user_id: The UUID of the user (for ownership validation).

        Returns:
            Conversation dictionary with:
            - session_id: UUID
            - created_at: datetime
            - updated_at: datetime
            - messages: list of message dicts with role, content, created_at

        Raises:
            ConversationServiceException: If retrieval fails or ownership validation fails.
        """
        time.time()

        try:
            # Get session and validate ownership
            session = await self._session_repository.get_by_id(session_id)
            if session is None:
                raise ConversationServiceException("Conversation not found")

            if session.user_id != user_id:
                pass
                raise ConversationServiceException("Conversation not found")

            # Get messages ordered chronologically (ASC from repository)
            messages = await self._message_repository.list_by_session(session_id)

            # Build message list
            message_list = [
                {
                    "id": message.id,
                    "role": message.role.value,
                    "content": message.content,
                    "created_at": message.created_at,
                }
                for message in messages
            ]

            result = {
                "session_id": session.id,
                "title": session.title,
                "document_ids": session.document_ids,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "messages": message_list,
            }

            pass

            return result

        except ConversationServiceException:
            raise
        except Exception as e:
            pass
            raise ConversationServiceException(f"Failed to get conversation: {e}")

    async def update_conversation(
        self,
        session_id: UUID,
        user_id: UUID,
        document_ids: list[str] | None = None,
        title: str | None = None,
    ) -> dict:
        """Update a conversation's document scope or title."""
        time.time()

        try:
            session = await self._session_repository.get_by_id(session_id)
            if session is None:
                raise ConversationServiceException("Conversation not found")

            if session.user_id != user_id:
                raise ConversationServiceException("Conversation not found")

            if title is not None:
                session.title = title
            if document_ids is not None:
                session.document_ids = document_ids

            await self._session_repository.update(session)

            return await self.get_conversation(session_id, user_id)

        except ConversationServiceException:
            raise
        except Exception as e:
            pass
            raise ConversationServiceException(f"Failed to update conversation: {e}")

    async def delete_conversation(self, session_id: UUID, user_id: UUID) -> None:
        """Delete a conversation.

        This deletes all messages first, then the session.
        Does not affect documents, vectors, chunks, or summaries.

        Args:
            session_id: The UUID of the conversation session.
            user_id: The UUID of the user (for ownership validation).

        Raises:
            ConversationServiceException: If deletion fails or ownership validation fails.
        """
        time.time()

        try:
            # Get session and validate ownership
            session = await self._session_repository.get_by_id(session_id)
            if session is None:
                raise ConversationServiceException("Conversation not found")

            if session.user_id != user_id:
                pass
                raise ConversationServiceException("Conversation not found")

            # Delete messages first
            await self._message_repository.delete_by_session(session_id)

            # Delete session
            await self._session_repository.delete(session_id)

            pass

        except ConversationServiceException:
            raise
        except Exception as e:
            pass
            raise ConversationServiceException(f"Failed to delete conversation: {e}")
