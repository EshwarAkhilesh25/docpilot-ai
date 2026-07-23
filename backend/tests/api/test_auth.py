from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.services.dto import AuthenticationResult
from app.services.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidUserDataException,
    UserAlreadyExistsException,
)
from app.services.interfaces.user import UserService

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_user_service():
    """Fixture for mocked UserService."""
    service = AsyncMock(spec=UserService)
    return service


@pytest.fixture
def mock_auth_service():
    """Fixture for mocked AuthenticationService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_user():
    """Fixture for a mock User entity."""
    user = MagicMock(spec=User)
    user.id = UUID("123e4567-e89b-12d3-a456-426614174000")
    user.full_name = "John Doe"
    user.email = "john@example.com"
    user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    user.is_active = True
    return user


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register endpoint."""

    def test_register_success(self, mock_user_service, mock_user):
        """Test successful user registration."""
        # Setup
        mock_user_service.register_user.return_value = mock_user

        from app.api.dependencies import get_user_service

        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 201
            assert response.json()["id"] == str(mock_user.id)
            assert response.json()["full_name"] == mock_user.full_name
            assert response.json()["email"] == mock_user.email
            assert response.json()["message"] == "Resource created successfully"
            mock_user_service.register_user.assert_called_once_with(
                full_name="John Doe",
                email="john@example.com",
                password="securePassword123",
            )
        finally:
            app.dependency_overrides.pop(get_user_service, None)

    def test_register_duplicate_email(self, mock_user_service):
        """Test registration with duplicate email returns 409."""
        # Setup
        mock_user_service.register_user.side_effect = UserAlreadyExistsException("john@example.com")

        from app.api.dependencies import get_user_service

        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 409
            assert "USER_ALREADY_EXISTS" in response.json()["error"]["code"]
            assert "already exists" in response.json()["error"]["message"]
        finally:
            app.dependency_overrides.pop(get_user_service, None)

    def test_register_invalid_request(self):
        """Test registration with invalid request data returns 422."""
        # Execute - missing password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "John Doe",
                "email": "john@example.com",
            },
        )

        # Assert
        assert response.status_code == 422

    def test_register_invalid_user_data(self, mock_user_service):
        """Test registration with invalid user data returns 400."""
        # Setup
        mock_user_service.register_user.side_effect = InvalidUserDataException("Invalid data")

        from app.api.dependencies import get_user_service

        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 400
            assert "INVALID_USER_DATA" in response.json()["error"]["code"]
        finally:
            app.dependency_overrides.pop(get_user_service, None)

    def test_register_unexpected_exception(self, mock_user_service):
        """Test registration with unexpected exception returns 500."""
        # Setup
        mock_user_service.register_user.side_effect = Exception("Database error")

        from app.api.dependencies import get_user_service

        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 500
        finally:
            app.dependency_overrides.pop(get_user_service, None)


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_success(self, mock_auth_service):
        """Test successful login."""
        # Setup
        mock_auth_service.login.return_value = AuthenticationResult(
            access_token="access_token",
            refresh_token="refresh_token",
            expires_in=3600,
        )

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == "access_token"
            assert response.json()["refresh_token"] == "refresh_token"
            assert response.json()["token_type"] == "bearer"
            assert response.json()["expires_in"] == 3600
            mock_auth_service.login.assert_called_once_with(
                email="john@example.com",
                password="securePassword123",
            )
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_login_invalid_credentials(self, mock_auth_service):
        """Test login with invalid credentials returns 401."""
        # Setup
        mock_auth_service.login.side_effect = InvalidCredentialsException("Invalid credentials")

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "john@example.com",
                    "password": "wrongpassword",
                },
            )

            # Assert
            assert response.status_code == 401
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_login_inactive_user(self, mock_auth_service):
        """Test login with inactive user returns 403."""
        # Setup
        mock_auth_service.login.side_effect = InactiveUserException("user_id")

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "john@example.com",
                    "password": "securePassword123",
                },
            )

            # Assert
            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_login_invalid_request(self):
        """Test login with invalid request data returns 422."""
        # Execute - missing password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "john@example.com",
            },
        )

        # Assert
        assert response.status_code == 422


class TestRefreshTokenEndpoint:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    def test_refresh_token_success(self, mock_auth_service):
        """Test successful token refresh."""
        # Setup
        mock_auth_service.refresh_token.return_value = AuthenticationResult(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            expires_in=3600,
        )

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "valid_refresh_token",
                },
            )

            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == "new_access_token"
            assert response.json()["refresh_token"] == "new_refresh_token"
            assert response.json()["token_type"] == "bearer"
            assert response.json()["expires_in"] == 3600
            mock_auth_service.refresh_token.assert_called_once_with(
                refresh_token="valid_refresh_token"
            )
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_refresh_token_invalid(self, mock_auth_service):
        """Test refresh with invalid token returns 401."""
        # Setup
        mock_auth_service.refresh_token.side_effect = InvalidCredentialsException("Invalid token")

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "invalid_token",
                },
            )

            # Assert
            assert response.status_code == 401
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_refresh_token_inactive_user(self, mock_auth_service):
        """Test refresh with inactive user returns 403."""
        # Setup
        mock_auth_service.refresh_token.side_effect = InactiveUserException("user_id")

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "valid_token",
                },
            )

            # Assert
            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)

    def test_refresh_token_invalid_request(self):
        """Test refresh with invalid request data returns 422."""
        # Execute - missing refresh_token
        response = client.post(
            "/api/v1/auth/refresh",
            json={},
        )

        # Assert
        assert response.status_code == 422


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout endpoint."""

    def test_logout_success(self, mock_auth_service):
        """Test successful logout."""
        # Setup
        mock_auth_service.logout = AsyncMock()

        from app.api.dependencies import get_authentication_service

        app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service

        try:
            # Execute
            response = client.post("/api/v1/auth/logout")

            # Assert
            assert response.status_code == 204
            assert response.content == b""
            mock_auth_service.logout.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_authentication_service, None)


class TestCurrentUserEndpoint:
    """Tests for GET /api/v1/auth/me endpoint."""

    def test_get_current_user_success(self, mock_user):
        """Test successful current user retrieval."""
        # Setup
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            # Execute
            response = client.get("/api/v1/auth/me")

            # Assert
            assert response.status_code == 200
            assert response.json()["id"] == str(mock_user.id)
            assert response.json()["full_name"] == mock_user.full_name
            assert response.json()["email"] == mock_user.email
            assert response.json()["is_active"] == mock_user.is_active
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_get_current_user_unauthorized(self):
        """Test current user retrieval without authentication returns 401."""
        # Execute - no authentication provided
        response = client.get("/api/v1/auth/me")

        # Assert - OAuth2PasswordBearer will return 401 if no token
        assert response.status_code == 401
