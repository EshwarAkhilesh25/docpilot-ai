"""Repository-specific exceptions for data access layer errors."""


class RepositoryException(Exception):
    """Base exception for repository errors."""

    pass


class EntityNotFoundException(RepositoryException):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_type: str, identifier: str):
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(f"{entity_type} with identifier '{identifier}' not found")


class DuplicateEntityException(RepositoryException):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, field: str, value: str):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f"{entity_type} with {field}='{value}' already exists")


class DatabaseOperationException(RepositoryException):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Database operation '{operation}' failed: {message}")
