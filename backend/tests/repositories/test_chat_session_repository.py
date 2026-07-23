"""Tests for ChatSessionRepository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.chat_session import ChatSession
from app.repositories.exceptions import EntityNotFoundException
from app.repositories.sqlalchemy.chat_session_repository import SQLAlchemyChatSessionRepository


@pytest.fixture
def mock_session():
    """Fixture for mocked SQLAlchemy session."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    # execute is an async method that returns a sync Result object
    session.execute = AsyncMock()
    session.execute.return_value = MagicMock()

    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Fixture for ChatSessionRepository."""
    return SQLAlchemyChatSessionRepository(mock_session)


class TestChatSessionRepository:
    """Tests for ChatSessionRepository."""

    @pytest.mark.asyncio
    async def test_create(self, repository, mock_session):
        """Test creating a chat session."""
        # Setup
        session = ChatSession(user_id=uuid4(), title="Test Session")

        # Execute
        await repository.create(session)

        # Assert
        mock_session.add.assert_called_once_with(session)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(session)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session):
        """Test getting a session by ID when found."""
        # Setup
        session_id = uuid4()
        session = ChatSession(id=session_id, user_id=uuid4(), title="Test")
        mock_session.execute.return_value.scalar_one_or_none.return_value = session

        # Execute
        result = await repository.get_by_id(session_id)

        # Assert
        assert result == session
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting a session by ID when not found."""
        # Setup
        session_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        result = await repository.get_by_id(session_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_user(self, repository, mock_session):
        """Test listing sessions by user ID."""
        # Setup
        user_id = uuid4()
        session1 = ChatSession(id=uuid4(), user_id=user_id, title="Session 1")
        session2 = ChatSession(id=uuid4(), user_id=user_id, title="Session 2")

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [session1, session2]
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.list_by_user(user_id)

        # Assert
        assert len(result) == 2
        assert result == [session1, session2]
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, repository, mock_session):
        """Test deleting a session."""
        # Setup
        session_id = uuid4()
        session = ChatSession(id=session_id, user_id=uuid4(), title="Test")
        mock_session.execute.return_value.scalar_one_or_none.return_value = session

        # Execute
        await repository.delete(session_id)

        # Assert
        mock_session.delete.assert_called_once_with(session)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting a session that doesn't exist."""
        # Setup
        session_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await repository.delete(session_id)

    @pytest.mark.asyncio
    async def test_exists_true(self, repository, mock_session):
        """Test exists when session exists."""
        # Setup
        session_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = session_id

        # Execute
        result = await repository.exists(session_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, repository, mock_session):
        """Test exists when session doesn't exist."""
        # Setup
        session_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        result = await repository.exists(session_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_list_with_message_info(self, repository, mock_session):
        """Test listing sessions with message info."""
        # Setup
        user_id = uuid4()
        session1 = ChatSession(id=uuid4(), user_id=user_id, title="Session 1")
        session2 = ChatSession(id=uuid4(), user_id=user_id, title="Session 2")

        # Mock the complex query result
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (session1, 5, "Last message 1"),
            (session2, 3, "Last message 2"),
        ]
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.list_with_message_info(user_id)

        # Assert
        assert len(result) == 2
        assert result[0]["session"] == session1
        assert result[0]["message_count"] == 5
        assert result[0]["last_message_preview"] == "Last message 1"
