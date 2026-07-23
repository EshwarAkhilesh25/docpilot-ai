from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import User


class UserService(ABC):
    """Abstract service interface for user-related business operations.

    This interface defines the contract for user business logic operations.
    Implementations should handle business rules, validation, and orchestration
    while delegating data access to repository implementations.
    """

    @abstractmethod
    async def register_user(
        self,
        *,
        full_name: str,
        email: str,
        password: str,
    ) -> User:
        """Register a new user in the system.

        Args:
            full_name: The user's full name.
            email: The user's email address.
            password: The user's password.

        Returns:
            The newly created User entity.

        Raises:
            ValidationError: If the request data is invalid.
            DuplicateError: If a user with the same email already exists.
        """

    @abstractmethod
    async def get_user_profile(self, user_id: UUID) -> User:
        """Retrieve the profile of a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The User entity.

        Raises:
            NotFoundError: If the user does not exist.
        """

    @abstractmethod
    async def update_user_profile(self, user_id: UUID, full_name: str) -> User:
        """Update a user's profile information.

        Args:
            user_id: The UUID of the user to update.
            full_name: The new full name for the user.

        Returns:
            The updated User entity.

        Raises:
            NotFoundError: If the user does not exist.
            ValidationError: If the update data is invalid.
        """

    @abstractmethod
    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user account.

        Args:
            user_id: The UUID of the user to deactivate.

        Returns:
            The deactivated User entity.

        Raises:
            NotFoundError: If the user does not exist.
        """

    @abstractmethod
    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        """Change a user's password.

        Args:
            user_id: The UUID of the user.
            current_password: The user's current password for verification.
            new_password: The new password to set.

        Raises:
            NotFoundError: If the user does not exist.
            ValidationError: If the current password is incorrect or new password is invalid.
        """
