"""Tests for ChatMessageRepository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.enums import ChatRole
from app.repositories.exceptions import EntityNotFoundException
from app.repositories.sqlalchemy.chat_message_repository import SQLAlchemyChatMessageRepository


@pytest.fixture
def mock_session():
    """Fixture for mocked SQLAlchemy session."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.execute.return_value = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Fixture for ChatMessageRepository."""
    return SQLAlchemyChatMessageRepository(mock_session)


class TestChatMessageRepository:
    """Tests for ChatMessageRepository."""

    @pytest.mark.asyncio
    async def test_create(self, repository, mock_session):
        """Test creating a chat message."""
        # Setup
        message = ChatMessage(session_id=uuid4(), role=ChatRole.USER, content="Hello")

        # Execute
        await repository.create(message)

        # Assert
        mock_session.add.assert_called_once_with(message)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session):
        """Test getting a message by ID when found."""
        # Setup
        message_id = uuid4()
        message = ChatMessage(
            id=message_id, session_id=uuid4(), role=ChatRole.USER, content="Hello"
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = message

        # Execute
        result = await repository.get_by_id(message_id)

        # Assert
        assert result == message

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting a message by ID when not found."""
        # Setup
        message_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        result = await repository.get_by_id(message_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_session(self, repository, mock_session):
        """Test listing messages by session ID."""
        # Setup
        session_id = uuid4()
        message1 = ChatMessage(
            id=uuid4(), session_id=session_id, role=ChatRole.USER, content="Hello"
        )
        message2 = ChatMessage(
            id=uuid4(), session_id=session_id, role=ChatRole.ASSISTANT, content="Hi there"
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [message1, message2]
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.list_by_session(session_id)

        # Assert
        assert len(result) == 2
        assert result == [message1, message2]
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_by_session(self, repository, mock_session):
        """Test deleting all messages for a session."""
        # Setup
        session_id = uuid4()

        # Execute
        await repository.delete_by_session(session_id)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, repository, mock_session):
        """Test deleting a message by ID."""
        # Setup
        message_id = uuid4()
        message = ChatMessage(
            id=message_id, session_id=uuid4(), role=ChatRole.USER, content="Hello"
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = message

        # Execute
        await repository.delete(message_id)

        # Assert
        mock_session.delete.assert_called_once_with(message)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting a message that doesn't exist."""
        # Setup
        message_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await repository.delete(message_id)
