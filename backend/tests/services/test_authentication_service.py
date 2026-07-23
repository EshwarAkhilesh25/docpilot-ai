from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from app.core.security import ExpiredTokenException, InvalidTokenException
from app.models.user import User
from app.services.authentication_service import AuthenticationServiceImpl
from app.services.dto import AuthenticationResult
from app.services.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
)


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_user():
    """Fixture for a mock User entity."""
    user = MagicMock(spec=User)
    user.id = UUID("123e4567-e89b-12d3-a456-426614174000")
    user.full_name = "John Doe"
    user.email = "john@example.com"
    user.hashed_password = "hashed_password"
    user.is_active = True
    return user


@pytest.fixture
def auth_service(mock_uow):
    """Fixture for AuthenticationServiceImpl."""
    return AuthenticationServiceImpl(mock_uow)


class TestLogin:
    """Tests for login method."""

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_uow, mock_user):
        """Test successful login."""
        # Setup
        mock_uow.user_repository.get_by_email.return_value = mock_user

        with patch("app.services.authentication_service.verify_password", return_value=True):
            with patch(
                "app.services.authentication_service.create_access_token",
                return_value="access_token",
            ):
                with patch(
                    "app.services.authentication_service.create_refresh_token",
                    return_value="refresh_token",
                ):
                    # Execute
                    result = await auth_service.login(
                        email="john@example.com", password="password123"
                    )

                    # Assert
                    assert isinstance(result, AuthenticationResult)
                    assert result.access_token == "access_token"
                    assert result.refresh_token == "refresh_token"
                    mock_uow.user_repository.get_by_email.assert_called_once_with(
                        "john@example.com"
                    )

    @pytest.mark.asyncio
    async def test_login_unknown_email(self, auth_service, mock_uow):
        """Test login with unknown email."""
        # Setup
        mock_uow.user_repository.get_by_email.return_value = None

        # Execute
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(email="unknown@example.com", password="password123")

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, auth_service, mock_uow, mock_user):
        """Test login with inactive user."""
        # Setup
        mock_user.is_active = False
        mock_uow.user_repository.get_by_email.return_value = mock_user

        # Execute
        with pytest.raises(InactiveUserException):
            await auth_service.login(email="john@example.com", password="password123")

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, auth_service, mock_uow, mock_user):
        """Test login with invalid password."""
        # Setup
        mock_uow.user_repository.get_by_email.return_value = mock_user

        with patch("app.services.authentication_service.verify_password", return_value=False):
            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.login(email="john@example.com", password="wrong_password")


class TestRefreshToken:
    """Tests for refresh_token method."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, mock_uow, mock_user):
        """Test successful token refresh."""
        # Setup
        mock_uow.user_repository.get_by_id.return_value = mock_user

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_user.id), "type": "refresh"}

            with patch(
                "app.services.authentication_service.create_access_token", return_value="new_access"
            ):
                with patch(
                    "app.services.authentication_service.create_refresh_token",
                    return_value="new_refresh",
                ):
                    # Execute
                    result = await auth_service.refresh_token(refresh_token="valid_refresh_token")

                    # Assert
                    assert isinstance(result, AuthenticationResult)
                    assert result.access_token == "new_access"
                    assert result.refresh_token == "new_refresh"
                    mock_uow.user_repository.get_by_id.assert_called_once_with(mock_user.id)

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(self, auth_service):
        """Test refresh with invalid token."""
        # Setup
        with patch(
            "app.services.authentication_service.decode_token",
            side_effect=InvalidTokenException("Invalid token"),
        ):
            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.refresh_token(refresh_token="invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_token_expired_token(self, auth_service):
        """Test refresh with expired token."""
        # Setup
        with patch(
            "app.services.authentication_service.decode_token",
            side_effect=ExpiredTokenException("Expired"),
        ):
            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.refresh_token(refresh_token="expired_token")

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(self, auth_service, mock_uow):
        """Test refresh with non-existent user."""
        # Setup
        mock_uow.user_repository.get_by_id.return_value = None

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {
                "sub": str(UUID("123e4567-e89b-12d3-a456-426614174000")),
                "type": "refresh",
            }

            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.refresh_token(refresh_token="valid_token")

    @pytest.mark.asyncio
    async def test_refresh_token_inactive_user(self, auth_service, mock_uow, mock_user):
        """Test refresh with inactive user."""
        # Setup
        mock_user.is_active = False
        mock_uow.user_repository.get_by_id.return_value = mock_user

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_user.id), "type": "refresh"}

            # Execute
            with pytest.raises(InactiveUserException):
                await auth_service.refresh_token(refresh_token="valid_token")


class TestVerifyToken:
    """Tests for verify_token method."""

    @pytest.mark.asyncio
    async def test_verify_token_success(self, auth_service, mock_uow, mock_user):
        """Test successful token verification."""
        # Setup
        mock_uow.user_repository.get_by_id.return_value = mock_user

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_user.id), "type": "access"}

            # Execute
            user = await auth_service.verify_token("valid_access_token")

            # Assert
            assert user == mock_user
            mock_uow.user_repository.get_by_id.assert_called_once_with(mock_user.id)

    @pytest.mark.asyncio
    async def test_verify_token_invalid_token(self, auth_service):
        """Test verify with invalid token."""
        # Setup
        with patch(
            "app.services.authentication_service.decode_token",
            side_effect=InvalidTokenException("Invalid"),
        ):
            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.verify_token("invalid_token")

    @pytest.mark.asyncio
    async def test_verify_token_expired_token(self, auth_service):
        """Test verify with expired token."""
        # Setup
        with patch(
            "app.services.authentication_service.decode_token",
            side_effect=ExpiredTokenException("Expired"),
        ):
            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.verify_token("expired_token")

    @pytest.mark.asyncio
    async def test_verify_token_user_not_found(self, auth_service, mock_uow):
        """Test verify with non-existent user."""
        # Setup
        mock_uow.user_repository.get_by_id.return_value = None

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {
                "sub": str(UUID("123e4567-e89b-12d3-a456-426614174000")),
                "type": "access",
            }

            # Execute
            with pytest.raises(InvalidCredentialsException):
                await auth_service.verify_token("valid_token")

    @pytest.mark.asyncio
    async def test_verify_token_inactive_user(self, auth_service, mock_uow, mock_user):
        """Test verify with inactive user."""
        # Setup
        mock_user.is_active = False
        mock_uow.user_repository.get_by_id.return_value = mock_user

        with patch("app.services.authentication_service.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_user.id), "type": "access"}

            # Execute
            with pytest.raises(InactiveUserException):
                await auth_service.verify_token("valid_token")


class TestLogout:
    """Tests for logout method."""

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service):
        """Test successful logout."""
        # Execute
        await auth_service.logout()

        # Assert - should not raise exception

    @pytest.mark.asyncio
    async def test_logout_success_no_validation(self, auth_service):
        """Test logout succeeds without token validation (stateless)."""
        # Execute
        await auth_service.logout()

        # Assert - should not raise exception (stateless JWT)
