from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class LLMProvider(ABC):
    """Abstract provider interface for Large Language Model operations.

    This interface defines the contract for LLM interactions across
    different providers (OpenAI, Anthropic, Groq, etc.). Implementations
    should handle backend-specific details while adhering to this interface.
    """

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a text completion.

        Args:
            prompt: The main prompt or user message.
            context: Optional conversation history or context documents.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            The generated text completion.

        Raises:
            LLMError: If generation fails.
        """

    @abstractmethod
    async def generate_completion_stream(
        self,
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a text completion with streaming.

        Args:
            prompt: The main prompt or user message.
            context: Optional conversation history or context documents.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            Chunks of generated text as they are produced.

        Raises:
            LLMError: If generation fails.
        """

    @abstractmethod
    async def generate_with_sources(
        self,
        prompt: str,
        context: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Generate a completion with source attribution.

        Args:
            prompt: The main prompt or user message.
            context: Conversation history and context documents.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            A tuple of (generated_text, source_documents).

        Raises:
            LLMError: If generation fails.
        """
