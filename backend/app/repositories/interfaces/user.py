from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import User


class UserRepository(ABC):
    """Abstract repository interface for User entity operations.

    This interface defines the contract for user data access operations.
    Implementations should handle database-specific details while adhering
    to this interface for consistency and testability.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: The User entity to create.

        Returns:
            The created User entity with generated fields populated.

        Raises:
            DatabaseError: If the creation fails due to database issues.
            DuplicateError: If a user with the same email already exists.
        """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The User entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The User entity if found, None otherwise.

        Raises:
            DatabaseError: If the query fails due to database issues.
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user in the database.

        Args:
            user: The User entity with updated fields.

        Returns:
            The updated User entity.

        Raises:
            DatabaseError: If the update fails due to database issues.
            NotFoundError: If the user does not exist.
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Delete a user by their unique identifier.

        Args:
            user_id: The UUID of the user to delete.

        Raises:
            DatabaseError: If the deletion fails due to database issues.
            NotFoundError: If the user does not exist.
        """
