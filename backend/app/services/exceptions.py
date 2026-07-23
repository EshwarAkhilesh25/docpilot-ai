"""Service-level exceptions for business logic errors."""


class ServiceException(Exception):
    """Base exception for service errors."""

    pass


class UserAlreadyExistsException(ServiceException):
    """Raised when attempting to register a user that already exists."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class UserNotFoundException(ServiceException):
    """Raised when a user is not found."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with id '{user_id}' not found")


class InvalidUserDataException(ServiceException):
    """Raised when user data is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class AuthenticationException(ServiceException):
    """Base exception for authentication errors."""

    pass


class InactiveUserException(AuthenticationException):
    """Raised when attempting to authenticate an inactive user."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with id '{user_id}' is inactive")


class InvalidCredentialsException(AuthenticationException):
    """Raised when authentication credentials are invalid."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class DocumentProcessingException(ServiceException):
    """Raised when document processing fails."""

    def __init__(self, message: str):
        super().__init__(message)


class DocumentServiceException(ServiceException):
    """Raised when document service operations fail."""

    def __init__(self, message: str):
        super().__init__(message)


class ConversationServiceException(ServiceException):
    """Raised when conversation operations fail."""

    def __init__(self, message: str):
        super().__init__(message)
