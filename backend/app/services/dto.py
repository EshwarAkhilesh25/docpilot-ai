"""Service-level Data Transfer Objects."""

from dataclasses import dataclass


@dataclass
class AuthenticationResult:
    """Result of authentication operation containing tokens."""

    access_token: str
    refresh_token: str
    expires_in: int
