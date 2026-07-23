"""Groq LLM provider implementation."""

import asyncio
import logging

import httpx

from app.chat.exceptions import LLMProviderException
from app.chat.interfaces.llm_provider import LLMProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqLLMProvider(LLMProvider):
    """Groq LLM provider for fast inference.

    This provider uses Groq's API for fast LLM inference with models
    like Llama 3.3-70B-Versatile. It maintains a single AsyncClient
    for all requests and supports graceful shutdown.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
    ):
        """Initialize the Groq LLM provider.

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY from config.
            model: Model to use for generation. If None, uses LLM_MODEL from config.
            timeout: Request timeout in seconds. If None, uses LLM_TIMEOUT from config.
            max_retries: Maximum number of retries. If None, uses LLM_MAX_RETRIES from config.
            retry_delay: Initial delay between retries. If None, uses LLM_RETRY_DELAY from config.
        """
        self._api_key = api_key or settings.GROQ_API_KEY
        self._model = model or settings.LLM_MODEL
        self._timeout = timeout or settings.LLM_TIMEOUT
        self._max_retries = max_retries or settings.LLM_MAX_RETRIES
        self._retry_delay = retry_delay or settings.LLM_RETRY_DELAY
        self._base_url = "https://api.groq.com/openai/v1"
        self._client: httpx.AsyncClient | None = None

        if not self._api_key:
            pass

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared AsyncClient.

        Returns:
            The shared AsyncClient instance.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        """Close the AsyncClient gracefully.

        This should be called during application shutdown.
        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes client."""
        await self.close()

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt to guide the model.
            max_tokens: Maximum number of tokens to generate. If None, uses LLM_MAX_TOKENS from config.
            temperature: Sampling temperature (0.0 to 1.0). If None, uses LLM_TEMPERATURE from config.

        Returns:
            The generated text response.

        Raises:
            LLMProviderException: If generation fails.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self._call_api_with_retry(
            messages=messages,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            temperature=temperature or settings.LLM_TEMPERATURE,
        )

    async def generate_with_history(
        self,
        messages: list[dict[str, str]],
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Generate a text response with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'.
                     Roles: 'system', 'user', 'assistant'.
            max_tokens: Maximum number of tokens to generate. If None, uses LLM_MAX_TOKENS from config.
            temperature: Sampling temperature (0.0 to 1.0). If None, uses LLM_TEMPERATURE from config.

        Returns:
            The generated text response.

        Raises:
            LLMProviderException: If generation fails.
        """
        return await self._call_api_with_retry(
            messages=messages,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            temperature=temperature or settings.LLM_TEMPERATURE,
        )

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
        from app.chat.prompts import get_summary_prompt

        system_prompt = get_summary_prompt()
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]

        return await self._call_api_with_retry(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    async def _call_api_with_retry(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Call Groq API with exponential backoff retry.

        Args:
            messages: List of messages for the API.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated text response.

        Raises:
            LLMProviderException: If all retries fail.
        """
        if not self._api_key:
            raise LLMProviderException("GROQ_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        last_error = None
        for attempt in range(self._max_retries):
            try:
                client = self._get_client()
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]

                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = self._retry_delay * (2**attempt)
                    pass
                    await asyncio.sleep(wait_time)
                    continue

                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                    raise LLMProviderException(
                        f"Groq API error (status {response.status_code}): {error_msg}"
                    )

            except httpx.TimeoutException as e:
                last_error = LLMProviderException(f"Groq API timeout: {e}")
                pass
                await asyncio.sleep(self._retry_delay * (2**attempt))

            except httpx.HTTPError as e:
                last_error = LLMProviderException(f"Groq API HTTP error: {e}")
                pass
                await asyncio.sleep(self._retry_delay * (2**attempt))

            except Exception as e:
                last_error = LLMProviderException(f"Unexpected error: {e}")
                pass
                break

        # All retries failed
        raise last_error or LLMProviderException("Failed to generate response after retries")
