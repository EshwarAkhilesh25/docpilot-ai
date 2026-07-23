"""Interface for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for LLM providers.

    This interface defines the contract for generating text responses
    from language models. Different implementations can use different
    providers (Groq, OpenAI, Anthropic, etc.).
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt to guide the model.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).

        Returns:
            The generated text response.

        Raises:
            LLMProviderException: If generation fails.
        """
        pass

    @abstractmethod
    async def generate_with_history(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate a text response with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'.
                     Roles: 'system', 'user', 'assistant'.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).

        Returns:
            The generated text response.

        Raises:
            LLMProviderException: If generation fails.
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        text: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> str:
        """Generate a summary of the provided text.

        Args:
            text: The text to summarize.
            max_tokens: Maximum number of tokens to generate for the summary.
            temperature: Sampling temperature (0.0 to 1.0), lower for more factual summaries.

        Returns:
            The generated summary.

        Raises:
            LLMProviderException: If generation fails.
        """
        pass
