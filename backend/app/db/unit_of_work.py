import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.interfaces.chat_message import ChatMessageRepository
from app.repositories.interfaces.chat_session import ChatSessionRepository
from app.repositories.interfaces.document import DocumentRepository
from app.repositories.interfaces.document_chunk import DocumentChunkRepository
from app.repositories.interfaces.document_content import DocumentContentRepository
from app.repositories.interfaces.processing_job import ProcessingJobRepository
from app.repositories.interfaces.user import UserRepository
from app.repositories.sqlalchemy.chat_message_repository import SQLAlchemyChatMessageRepository
from app.repositories.sqlalchemy.chat_session_repository import SQLAlchemyChatSessionRepository
from app.repositories.sqlalchemy.document_chunk_repository import SQLAlchemyDocumentChunkRepository
from app.repositories.sqlalchemy.document_content_repository import (
    SQLAlchemyDocumentContentRepository,
)
from app.repositories.sqlalchemy.document_repository import SQLAlchemyDocumentRepository
from app.repositories.sqlalchemy.processing_job_repository import SQLAlchemyProcessingJobRepository
from app.repositories.sqlalchemy.user_repository import SQLAlchemyUserRepository

logger = logging.getLogger(__name__)


class IUnitOfWork(ABC):
    """Abstract Unit of Work interface for transaction management.

    This interface defines the contract for managing database transactions
    and providing access to repositories. Implementations should handle
    transaction lifecycle (commit, rollback, close) and lazily initialize
    repositories.
    """

    @property
    @abstractmethod
    def user_repository(self) -> UserRepository:
        """Get the user repository."""
        pass

    @property
    @abstractmethod
    def document_repository(self) -> DocumentRepository:
        """Get the document repository."""
        pass

    @property
    @abstractmethod
    def chat_session_repository(self) -> ChatSessionRepository:
        """Get the chat session repository."""
        pass

    @property
    @abstractmethod
    def chat_message_repository(self) -> ChatMessageRepository:
        """Get the chat message repository."""
        pass

    @property
    @abstractmethod
    def processing_job_repository(self) -> ProcessingJobRepository:
        """Get the processing job repository."""
        pass

    @property
    @abstractmethod
    def document_content_repository(self) -> DocumentContentRepository:
        """Get the document content repository."""
        pass

    @property
    @abstractmethod
    def document_chunk_repository(self) -> DocumentChunkRepository:
        """Get the document chunk repository."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the database session."""
        pass

    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work.

    This class manages database transactions and provides lazy-initialized
    repository instances. It implements the async context manager protocol
    for automatic session cleanup.

    Usage:
        async with SQLAlchemyUnitOfWork(session) as uow:
            user = await uow.user_repository.create(user_entity)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession):
        """Initialize Unit of Work with an existing AsyncSession.

        Args:
            session: An existing AsyncSession instance.
        """
        self._session = session
        self._user_repository: UserRepository | None = None
        self._document_repository: DocumentRepository | None = None
        self._chat_session_repository: ChatSessionRepository | None = None
        self._chat_message_repository: ChatMessageRepository | None = None
        self._processing_job_repository: ProcessingJobRepository | None = None
        self._document_content_repository: DocumentContentRepository | None = None
        self._document_chunk_repository: DocumentChunkRepository | None = None

    @property
    def user_repository(self) -> UserRepository:
        """Get the user repository (lazy initialization)."""
        if self._user_repository is None:
            self._user_repository = SQLAlchemyUserRepository(self._session)
        return self._user_repository

    @property
    def document_repository(self) -> DocumentRepository:
        """Get the document repository (lazy initialization)."""
        if self._document_repository is None:
            self._document_repository = SQLAlchemyDocumentRepository(self._session)
        return self._document_repository

    @property
    def chat_session_repository(self) -> ChatSessionRepository:
        """Get the chat session repository (lazy initialization)."""
        if self._chat_session_repository is None:
            self._chat_session_repository = SQLAlchemyChatSessionRepository(self._session)
        return self._chat_session_repository

    @property
    def chat_message_repository(self) -> ChatMessageRepository:
        """Get the chat message repository (lazy initialization)."""
        if self._chat_message_repository is None:
            self._chat_message_repository = SQLAlchemyChatMessageRepository(self._session)
        return self._chat_message_repository

    @property
    def processing_job_repository(self) -> ProcessingJobRepository:
        """Get the processing job repository (lazy initialization)."""
        if self._processing_job_repository is None:
            self._processing_job_repository = SQLAlchemyProcessingJobRepository(self._session)
        return self._processing_job_repository

    @property
    def document_content_repository(self) -> DocumentContentRepository:
        """Get the document content repository (lazy initialization)."""
        if self._document_content_repository is None:
            self._document_content_repository = SQLAlchemyDocumentContentRepository(self._session)
        return self._document_content_repository

    @property
    def document_chunk_repository(self) -> DocumentChunkRepository:
        """Get the document chunk repository (lazy initialization)."""
        if self._document_chunk_repository is None:
            self._document_chunk_repository = SQLAlchemyDocumentChunkRepository(self._session)
        return self._document_chunk_repository

    async def commit(self) -> None:
        """Commit the current transaction."""
        try:
            await self._session.commit()
        except Exception:
            pass
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        try:
            await self._session.rollback()
        except Exception:
            pass

    async def close(self) -> None:
        """Close the database session."""
        try:
            await self._session.close()
        except Exception:
            pass
        finally:
            self._user_repository = None
            self._document_repository = None
            self._chat_session_repository = None
            self._chat_message_repository = None
            self._processing_job_repository = None
            self._document_content_repository = None
            self._document_chunk_repository = None

    async def __aenter__(self) -> IUnitOfWork:
        """Async context manager entry.

        Returns:
            The Unit of Work instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Rolls back if an exception occurred. Always closes the session.
        """
        if exc_type is not None:
            await self.rollback()
        await self.close()


class UnitOfWorkFactory:
    """Factory for creating UnitOfWork instances.

    This factory ensures each transaction gets a fresh UnitOfWork
    with a new AsyncSession, preventing session reuse issues.
    """

    @staticmethod
    def create() -> IUnitOfWork:
        """Create a new UnitOfWork instance with a fresh session.

        Returns:
            A new SQLAlchemyUnitOfWork instance.
        """
        session = AsyncSessionLocal()
        return SQLAlchemyUnitOfWork(session)
