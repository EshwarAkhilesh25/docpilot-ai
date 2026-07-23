import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.exceptions import (
    DatabaseOperationException,
    DuplicateEntityException,
    EntityNotFoundException,
)
from app.repositories.interfaces.user import UserRepository

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy 2.0 async implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with async session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self._session = session

    async def create(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: The User entity to create.

        Returns:
            The created User entity with generated fields populated.

        Raises:
            DuplicateEntityException: If a user with the same email already exists.
            DatabaseOperationException: If the creation fails due to database issues.
        """
        try:
            self._session.add(user)
            await self._session.flush()
            await self._session.refresh(user)
            pass
            return user
        except IntegrityError as e:
            if "email" in str(e.orig):
                pass
                raise DuplicateEntityException("User", "email", user.email) from e
            pass
            raise DatabaseOperationException("create", str(e)) from e
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("create", str(e)) from e

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The User entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self._session.execute(stmt)
            user = result.scalar_one_or_none()

            return user
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_by_id", str(e)) from e

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The User entity if found, None otherwise.

        Raises:
            DatabaseOperationException: If the query fails due to database issues.
        """
        try:
            stmt = select(User).where(User.email == email)
            result = await self._session.execute(stmt)
            user = result.scalar_one_or_none()

            return user
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("get_by_email", str(e)) from e

    async def update(self, user: User) -> User:
        """Update an existing user in the database.

        Args:
            user: The User entity with updated fields.

        Returns:
            The updated User entity.

        Raises:
            EntityNotFoundException: If the user does not exist.
            DatabaseOperationException: If the update fails due to database issues.
        """
        try:
            # Check if user exists
            existing = await self.get_by_id(user.id)
            if existing is None:
                pass
                raise EntityNotFoundException("User", str(user.id))

            # Merge updates using async pattern
            merged = await self._session.merge(user)
            await self._session.flush()
            await self._session.refresh(merged)
            pass
            return merged
        except EntityNotFoundException:
            raise
        except IntegrityError as e:
            if "email" in str(e.orig):
                pass
                raise DuplicateEntityException("User", "email", user.email) from e
            pass
            raise DatabaseOperationException("update", str(e)) from e
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("update", str(e)) from e

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by their unique identifier.

        Args:
            user_id: The UUID of the user to delete.

        Raises:
            EntityNotFoundException: If the user does not exist.
            DatabaseOperationException: If the deletion fails due to database issues.
        """
        try:
            user = await self.get_by_id(user_id)
            if user is None:
                pass
                raise EntityNotFoundException("User", str(user_id))

            await self._session.delete(user)
            await self._session.flush()
            pass
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            pass
            raise DatabaseOperationException("delete", str(e)) from e
