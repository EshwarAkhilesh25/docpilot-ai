from abc import ABC, abstractmethod

from app.models.user import User
from app.services.dto import AuthenticationResult


class AuthenticationService(ABC):
    """Abstract service interface for authentication operations.

    This interface defines the contract for authentication business logic.
    Implementations should handle token generation, validation, and user
    authentication while delegating data access to repository implementations.
    """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    async def logout(self) -> None:
        """Logout a user.

        Stateless JWT - no blacklist implementation.
        Token will be invalid after expiration.
        """

    @abstractmethod
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
