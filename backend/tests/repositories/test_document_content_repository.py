"""Tests for SQLAlchemyDocumentContentRepository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.document_content import DocumentContent
from app.repositories.exceptions import EntityNotFoundException
from app.repositories.sqlalchemy.document_content_repository import (
    SQLAlchemyDocumentContentRepository,
)


@pytest.fixture
def mock_session():
    """Fixture for mocked AsyncSession."""
    session = AsyncMock()
    return session


class TestSQLAlchemyDocumentContentRepository:
    """Tests for SQLAlchemyDocumentContentRepository."""

    def test_init(self, mock_session):
        """Test repository initialization."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        assert repo._session is mock_session

    @pytest.mark.asyncio
    async def test_create(self, mock_session):
        """Test creating a document content record."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content = MagicMock(spec=DocumentContent)
        content.id = uuid4()

        # Execute
        result = await repo.create(content)

        # Assert
        mock_session.add.assert_called_once_with(content)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(content)
        assert result is content

    @pytest.mark.asyncio
    async def test_get_by_id(self, mock_session):
        """Test retrieving document content by ID."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content_id = uuid4()
        content = MagicMock(spec=DocumentContent)

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = content
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repo.get_by_id(content_id)

        # Assert
        assert result is content

    @pytest.mark.asyncio
    async def test_get_by_document_id(self, mock_session):
        """Test retrieving document content by document ID."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        document_id = uuid4()
        content = MagicMock(spec=DocumentContent)

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = content
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repo.get_by_document_id(document_id)

        # Assert
        assert result is content

    @pytest.mark.asyncio
    async def test_update(self, mock_session):
        """Test updating a document content record."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content = MagicMock(spec=DocumentContent)
        content.id = uuid4()

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = content
        mock_session.execute.return_value = mock_result
        mock_session.merge.return_value = content

        # Execute
        result = await repo.update(content)

        # Assert
        mock_session.merge.assert_called_once_with(content)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(content)
        assert result is content

    @pytest.mark.asyncio
    async def test_update_not_found(self, mock_session):
        """Test updating when content is not found."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content = MagicMock(spec=DocumentContent)
        content.id = uuid4()

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await repo.update(content)

    @pytest.mark.asyncio
    async def test_delete(self, mock_session):
        """Test deleting a document content record."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content_id = uuid4()
        content = MagicMock(spec=DocumentContent)

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = content
        mock_session.execute.return_value = mock_result

        # Execute
        await repo.delete(content_id)

        # Assert
        mock_session.delete.assert_called_once_with(content)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_session):
        """Test deleting when content is not found."""
        repo = SQLAlchemyDocumentContentRepository(mock_session)
        content_id = uuid4()

        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await repo.delete(content_id)
