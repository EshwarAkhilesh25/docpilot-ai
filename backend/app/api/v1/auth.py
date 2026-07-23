import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    AuthenticationServiceDep,
    get_current_user,
    get_user_service,
)
from app.core.constants import MSG_CREATED
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    UpdateProfileRequest,
)
from app.services.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
)
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with the provided credentials.",
)
async def register(
    request: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
) -> RegisterResponse:
    """Register a new user.

    Args:
        request: Registration request with user details.
        user_service: Injected user service.

    Returns:
        RegisterResponse with created user details.

    Raises:
        UserAlreadyExistsException: If user with email already exists (HTTP 409).
        InvalidUserDataException: If request data is invalid (HTTP 400).
    """
    user = await user_service.register_user(
        full_name=request.full_name,
        email=request.email,
        password=request.password,
    )

    return RegisterResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        created_at=user.created_at,
        message=MSG_CREATED,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate a user with email and password and return JWT tokens.",
)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationServiceDep,
) -> LoginResponse:
    """Login a user and return authentication tokens.

    Args:
        request: Login request with email and password.
        auth_service: Injected authentication service.

    Returns:
        LoginResponse with access and refresh tokens.

    Raises:
        HTTPException: If credentials are invalid (HTTP 401) or user is inactive (HTTP 403).
    """
    pass

    try:
        result = await auth_service.login(email=request.email, password=request.password)
    except InvalidCredentialsException as e:
        pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except InactiveUserException as e:
        pass
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    pass

    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type="bearer",
        expires_in=result.expires_in,
    )


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
    description="Refresh an access token using a valid refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthenticationServiceDep,
) -> LoginResponse:
    """Refresh an access token.

    Args:
        request: Refresh token request.
        auth_service: Injected authentication service.

    Returns:
        LoginResponse with new access and refresh tokens.

    Raises:
        InvalidCredentialsException: If refresh token is invalid or expired (HTTP 401).
        InactiveUserException: If the user is inactive (HTTP 403).
    """
    try:
        result = await auth_service.refresh_token(refresh_token=request.refresh_token)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except InactiveUserException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    pass

    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type="bearer",
        expires_in=result.expires_in,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Logout the current user. Stateless JWT - token will be invalid after expiration.",
)
async def logout(auth_service: AuthenticationServiceDep) -> None:
    """Logout a user.

    Args:
        auth_service: Injected authentication service.

    Returns:
        HTTP 204 No Content.

    Note:
        This is a stateless JWT implementation. The token will be invalid
        after its expiration time. No token blacklist is maintained.
    """
    pass
    await auth_service.logout()
    pass


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    """Get current user information.

    Args:
        current_user: Injected authenticated user from dependency.

    Returns:
        CurrentUserResponse with user information.
    """
    return CurrentUserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )


@router.put(
    "/me",
    response_model=CurrentUserResponse,
    summary="Update current user profile",
    description="Update the currently authenticated user's profile information.",
)
async def update_current_user_profile(
    request: UpdateProfileRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    """Update current user profile.

    Args:
        request: Update profile request with new full name.
        current_user: Injected authenticated user from dependency.
        user_service: Injected user service.

    Returns:
        CurrentUserResponse with updated user information.

    Raises:
        UserNotFoundException: If the user does not exist (HTTP 404).
        InvalidUserDataException: If the update data is invalid (HTTP 400).
    """
    pass

    updated_user = await user_service.update_user_profile(
        user_id=current_user.id,
        full_name=request.full_name,
    )

    pass

    return CurrentUserResponse(
        id=updated_user.id,
        full_name=updated_user.full_name,
        email=updated_user.email,
        created_at=updated_user.created_at,
        is_active=updated_user.is_active,
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change the currently authenticated user's password.",
)
async def change_password(
    request: ChangePasswordRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Change current user password.

    Args:
        request: Change password request with current and new passwords.
        current_user: Injected authenticated user from dependency.
        user_service: Injected user service.

    Returns:
        HTTP 204 No Content.

    Raises:
        UserNotFoundException: If the user does not exist (HTTP 404).
        InvalidUserDataException: If the current password is incorrect or new password is invalid (HTTP 400).
    """
    pass

    await user_service.change_password(
        user_id=current_user.id,
        current_password=request.current_password,
        new_password=request.new_password,
    )

    pass
