from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password",
        examples=["securePassword123"],
    )


class LoginResponse(BaseModel):
    """Response schema for user login."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Type of the token",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[3600],
    )


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    full_name: str = Field(
        min_length=1,
        max_length=255,
        description="User's full name",
        examples=["John Doe"],
    )
    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)",
        examples=["securePassword123"],
    )


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Type of the token",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[3600],
    )


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(
        description="Valid refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class RegisterResponse(BaseModel):
    """Response schema for user registration."""

    id: UUID = Field(description="User ID")
    full_name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    created_at: datetime = Field(description="Account creation timestamp")
    message: str = Field(default="User registered successfully")


class CurrentUserResponse(BaseModel):
    """Response schema for current user information."""

    id: UUID = Field(description="User ID")
    full_name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    created_at: datetime = Field(description="Account creation timestamp")
    is_active: bool = Field(description="Whether the user account is active")


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""

    full_name: str = Field(
        min_length=2,
        max_length=255,
        description="User's full name",
        examples=["John Doe"],
    )


class ChangePasswordRequest(BaseModel):
    """Request schema for changing user password."""

    current_password: str = Field(
        min_length=8,
        max_length=128,
        description="Current password for verification",
        examples=["oldPassword123"],
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password to set",
        examples=["newSecurePassword456"],
    )
