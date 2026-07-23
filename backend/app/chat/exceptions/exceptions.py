"""Exceptions for chat operations."""


class ChatException(Exception):
    """Base exception for chat operations.

    This exception is raised when there is a general error in chat operations.
    """

    pass


class LLMProviderException(ChatException):
    """Exception raised when LLM provider fails.

    This exception is raised when the LLM provider encounters an error
    during text generation.
    """

    pass


class ContextLengthExceededException(ChatException):
    """Exception raised when context length exceeds model limits.

    This exception is raised when the combined context (retrieved chunks +
    conversation history) exceeds the model's context window.
    """

    pass
