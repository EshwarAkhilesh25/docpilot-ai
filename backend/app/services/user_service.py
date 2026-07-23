import logging
from uuid import UUID

from app.core.security import hash_password, verify_password
from app.db.unit_of_work import IUnitOfWork
from app.models.user import User
from app.services.exceptions import (
    InvalidUserDataException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.services.interfaces.user import UserService

logger = logging.getLogger(__name__)


class UserServiceImpl(UserService):
    """Implementation of UserService for user business operations."""

    def __init__(self, uow: IUnitOfWork):
        """Initialize service with Unit of Work.

        Args:
            uow: Unit of Work for transaction management.
        """
        self._uow = uow

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
            UserAlreadyExistsException: If a user with the same email already exists.
        """
        # Check if user already exists
        async with self._uow:
            existing_user = await self._uow.user_repository.get_by_email(email)
            if existing_user is not None:
                pass
                raise UserAlreadyExistsException(email)

            # Hash password
            hashed_password = hash_password(password)

            # Create user entity
            user = User(
                full_name=full_name,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
            )

            # Persist via repository
            created_user = await self._uow.user_repository.create(user)
            await self._uow.commit()

            pass

            return created_user

    async def get_user_profile(self, user_id: UUID) -> User:
        """Retrieve the profile of a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The User entity.

        Raises:
            UserNotFoundException: If the user does not exist.
        """
        async with self._uow:
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                raise UserNotFoundException(str(user_id))

            return user

    async def update_user_profile(self, user_id: UUID, full_name: str) -> User:
        """Update a user's profile information.

        Args:
            user_id: The UUID of the user to update.
            full_name: The new full name for the user.

        Returns:
            The updated User entity.

        Raises:
            UserNotFoundException: If the user does not exist.
            InvalidUserDataException: If the update data is invalid.
        """
        async with self._uow:
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                raise UserNotFoundException(str(user_id))

            # Apply update
            user.full_name = full_name

            # Persist via repository
            updated_user = await self._uow.user_repository.update(user)
            await self._uow.commit()

            pass

            return updated_user

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user account.

        Args:
            user_id: The UUID of the user to deactivate.

        Returns:
            The deactivated User entity.

        Raises:
            UserNotFoundException: If the user does not exist.
        """
        async with self._uow:
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                raise UserNotFoundException(str(user_id))

            user.is_active = False

            # Persist via repository
            deactivated_user = await self._uow.user_repository.update(user)
            await self._uow.commit()

            pass

            return deactivated_user

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        """Change a user's password.

        Args:
            user_id: The UUID of the user.
            current_password: The user's current password for verification.
            new_password: The new password to set.

        Raises:
            UserNotFoundException: If the user does not exist.
            InvalidUserDataException: If the current password is incorrect or new password is invalid.
        """
        async with self._uow:
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                raise UserNotFoundException(str(user_id))

            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                pass
                raise InvalidUserDataException("Current password is incorrect")

            # Prevent changing to the same password
            if verify_password(new_password, user.hashed_password):
                pass
                raise InvalidUserDataException(
                    "New password must be different from current password"
                )

            # Hash new password
            hashed_password = hash_password(new_password)
            user.hashed_password = hashed_password

            # Persist via repository
            await self._uow.user_repository.update(user)
            await self._uow.commit()

            pass
