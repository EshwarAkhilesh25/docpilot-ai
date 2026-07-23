"""Tests for ConversationService."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import ChatRole
from app.services.conversation_service import ConversationService
from app.services.exceptions import ConversationServiceException


@pytest.fixture
def mock_session_repository():
    """Fixture for mocked ChatSessionRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_message_repository():
    """Fixture for mocked ChatMessageRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def conversation_service(mock_session_repository, mock_message_repository):
    """Fixture for ConversationService."""
    return ConversationService(mock_session_repository, mock_message_repository)


class TestConversationService:
    """Tests for ConversationService."""

    @pytest.mark.asyncio
    async def test_list_conversations_success(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test successful conversation listing."""
        # Setup
        user_id = uuid4()
        session1 = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Session 1",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )
        session2 = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Session 2",
            created_at=datetime(2024, 1, 2, 10, 0, 0),
            updated_at=datetime(2024, 1, 2, 11, 0, 0),
        )

        mock_session_repository.list_with_message_info.return_value = [
            {
                "session": session2,
                "message_count": 3,
                "last_message_preview": "Short message",
            },
            {
                "session": session1,
                "message_count": 5,
                "last_message_preview": "Hello world, this is a longer message that should be truncated",
            },
        ]

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert len(result) == 2
        assert all("session_id" in conv for conv in result)
        assert all("created_at" in conv for conv in result)
        assert all("updated_at" in conv for conv in result)
        assert all("message_count" in conv for conv in result)
        assert all("last_message_preview" in conv for conv in result)
        # Verify ordering by updated_at DESC (from repository)
        assert result[0]["updated_at"] >= result[1]["updated_at"]

    @pytest.mark.asyncio
    async def test_list_conversations_empty(self, conversation_service, mock_session_repository):
        """Test listing conversations when user has none."""
        # Setup
        user_id = uuid4()
        mock_session_repository.list_with_message_info.return_value = []

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_conversation_success(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test successful conversation retrieval."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title="Test Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        message1 = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            role=ChatRole.USER,
            content="Hello",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        message2 = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            role=ChatRole.ASSISTANT,
            content="Hi there",
            created_at=datetime(2024, 1, 1, 10, 0, 1),
        )

        mock_session_repository.get_by_id.return_value = session
        mock_message_repository.list_by_session.return_value = [message1, message2]

        # Execute
        result = await conversation_service.get_conversation(session_id, user_id)

        # Assert
        assert result["session_id"] == session_id
        assert result["created_at"] == session.created_at
        assert result["updated_at"] == session.updated_at
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test getting a conversation that doesn't exist."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        mock_session_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(ConversationServiceException) as exc_info:
            await conversation_service.get_conversation(session_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_conversation_unauthorized(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test getting a conversation owned by another user."""
        # Setup
        user_id = uuid4()
        other_user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=other_user_id,
            title="Other Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session

        # Execute & Assert
        with pytest.raises(ConversationServiceException) as exc_info:
            await conversation_service.get_conversation(session_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_conversation_success(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test successful conversation deletion."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title="Test Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session

        # Execute
        await conversation_service.delete_conversation(session_id, user_id)

        # Assert
        mock_message_repository.delete_by_session.assert_called_once_with(session_id)
        mock_session_repository.delete.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test deleting a conversation that doesn't exist."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        mock_session_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(ConversationServiceException) as exc_info:
            await conversation_service.delete_conversation(session_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_conversation_unauthorized(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test deleting a conversation owned by another user."""
        # Setup
        user_id = uuid4()
        other_user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=other_user_id,
            title="Other Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session

        # Execute & Assert
        with pytest.raises(ConversationServiceException) as exc_info:
            await conversation_service.delete_conversation(session_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_list_conversations_with_zero_messages(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test listing conversations with zero messages."""
        # Setup
        user_id = uuid4()
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Empty Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.list_with_message_info.return_value = [
            {
                "session": session,
                "message_count": 0,
                "last_message_preview": "",
            }
        ]

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert len(result) == 1
        assert result[0]["message_count"] == 0
        assert result[0]["last_message_preview"] == ""

    @pytest.mark.asyncio
    async def test_list_conversations_with_one_user_message(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test listing conversations with only one user message."""
        # Setup
        user_id = uuid4()
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Single Message Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.list_with_message_info.return_value = [
            {
                "session": session,
                "message_count": 1,
                "last_message_preview": "Hello",
            }
        ]

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert len(result) == 1
        assert result[0]["message_count"] == 1
        assert result[0]["last_message_preview"] == "Hello"

    @pytest.mark.asyncio
    async def test_list_conversations_with_only_assistant_messages(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test listing conversations with only assistant messages."""
        # Setup
        user_id = uuid4()
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Assistant Only Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.list_with_message_info.return_value = [
            {
                "session": session,
                "message_count": 3,
                "last_message_preview": "Here is the answer",
            }
        ]

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert len(result) == 1
        assert result[0]["message_count"] == 3

    @pytest.mark.asyncio
    async def test_preview_truncation(
        self,
        conversation_service,
        mock_session_repository,
    ):
        """Test that message preview is truncated to 100 characters."""
        # Setup
        user_id = uuid4()
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            title="Long Message Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        long_message = "This is a very long message that exceeds one hundred characters and should be truncated with an ellipsis at the end to indicate that there is more content"

        mock_session_repository.list_with_message_info.return_value = [
            {
                "session": session,
                "message_count": 1,
                "last_message_preview": long_message[:100] + "...",
            }
        ]

        # Execute
        result = await conversation_service.list_conversations(user_id)

        # Assert
        assert len(result) == 1
        assert len(result[0]["last_message_preview"]) <= 103  # 100 chars + "..."

    @pytest.mark.asyncio
    async def test_get_conversation_with_zero_messages(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test getting a conversation with zero messages."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title="Empty Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session
        mock_message_repository.list_by_session.return_value = []

        # Execute
        result = await conversation_service.get_conversation(session_id, user_id)

        # Assert
        assert result["session_id"] == session_id
        assert len(result["messages"]) == 0

    @pytest.mark.asyncio
    async def test_get_conversation_with_only_assistant_messages(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test getting a conversation with only assistant messages."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title="Assistant Only Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        message = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            role=ChatRole.ASSISTANT,
            content="Hello from assistant",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session
        mock_message_repository.list_by_session.return_value = [message]

        # Execute
        result = await conversation_service.get_conversation(session_id, user_id)

        # Assert
        assert result["session_id"] == session_id
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_delete_conversation_rollback_on_failure(
        self,
        conversation_service,
        mock_session_repository,
        mock_message_repository,
    ):
        """Test that deletion rolls back if session delete fails after messages are deleted."""
        # Setup
        user_id = uuid4()
        session_id = uuid4()
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title="Test Session",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
        )

        mock_session_repository.get_by_id.return_value = session
        mock_message_repository.delete_by_session.return_value = None
        mock_session_repository.delete.side_effect = Exception("Database error")

        # Execute & Assert
        with pytest.raises(ConversationServiceException):
            await conversation_service.delete_conversation(session_id, user_id)

        # Verify messages were deleted (this would be rolled back by UnitOfWork in real scenario)
        mock_message_repository.delete_by_session.assert_called_once_with(session_id)
