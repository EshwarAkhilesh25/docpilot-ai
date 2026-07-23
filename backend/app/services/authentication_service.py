import logging
from uuid import UUID

from app.core.config import get_settings
from app.core.security import (
    ExpiredTokenException,
    InvalidTokenException,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.unit_of_work import IUnitOfWork
from app.models.user import User
from app.services.dto import AuthenticationResult
from app.services.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
)
from app.services.interfaces.auth import AuthenticationService

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthenticationServiceImpl(AuthenticationService):
    """Implementation of AuthenticationService for authentication operations."""

    def __init__(self, uow: IUnitOfWork):
        """Initialize service with Unit of Work.

        Args:
            uow: Unit of Work for transaction management.
        """
        self._uow = uow

    async def login(self, *, email: str, password: str) -> AuthenticationResult:
        """Authenticate a user and return tokens.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            AuthenticationResult containing access and refresh tokens.

        Raises:
            InvalidCredentialsException: If credentials are invalid.
            InactiveUserException: If the user is inactive.
        """
        async with self._uow:
            # Retrieve user by email
            user = await self._uow.user_repository.get_by_email(email)
            if user is None:
                pass
                raise InvalidCredentialsException("Invalid email or password")

            # Verify user is active
            if not user.is_active:
                pass
                raise InactiveUserException(str(user.id))

            # Verify password
            if not verify_password(password, user.hashed_password):
                pass
                raise InvalidCredentialsException("Invalid email or password")

            # Create tokens
            access_token = create_access_token(subject=str(user.id))
            refresh_token = create_refresh_token(subject=str(user.id))

            pass

            return AuthenticationResult(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

    async def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token string.

        Returns:
            AuthenticationResult containing new access and refresh tokens.

        Raises:
            InvalidCredentialsException: If the refresh token is invalid or expired.
            InactiveUserException: If the user is inactive.
        """
        try:
            # Decode and validate refresh token
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = UUID(payload["sub"])
        except (InvalidTokenException, ExpiredTokenException):
            pass
            raise InvalidCredentialsException("Invalid or expired refresh token")

        async with self._uow:
            # Retrieve user
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                raise InvalidCredentialsException("Invalid refresh token")

            # Verify user is active
            if not user.is_active:
                pass
                raise InactiveUserException(str(user_id))

            # Issue new tokens
            access_token = create_access_token(subject=str(user.id))
            new_refresh_token = create_refresh_token(subject=str(user.id))

            pass

            return AuthenticationResult(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

    async def verify_token(self, token: str) -> User:
        """Verify a token and return the user.

        Args:
            token: The access token to verify.

        Returns:
            The User entity associated with the token.

        Raises:
            InvalidCredentialsException: If the token is invalid or expired.
            InactiveUserException: If the user is inactive.
        """
        try:
            pass
            pass
            # Decode and validate access token
            payload = decode_token(token, expected_type="access")
            pass
            pass
            user_id = UUID(payload["sub"])
            pass
        except (InvalidTokenException, ExpiredTokenException):
            pass
            pass
            raise InvalidCredentialsException("Invalid or expired access token")

        pass
        async with self._uow:
            pass
            # Retrieve user
            user = await self._uow.user_repository.get_by_id(user_id)
            if user is None:
                pass
                pass
                raise InvalidCredentialsException("Invalid access token")

            # Verify user is active
            if not user.is_active:
                pass
                raise InactiveUserException(str(user_id))

            return user

    async def logout(self) -> None:
        """Logout a user.

        Stateless JWT - no blacklist implementation.
        Token will be invalid after expiration.
        """
        pass
