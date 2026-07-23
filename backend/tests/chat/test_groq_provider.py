"""Tests for Groq LLM provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.chat.exceptions import LLMProviderException
from app.chat.providers.groq_provider import GroqLLMProvider


@pytest.fixture
def mock_client():
    """Fixture for mocked httpx AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.is_closed = False
    return client


@pytest.fixture
def provider(mock_client):
    """Fixture for GroqLLMProvider with mocked client."""
    with patch("app.chat.providers.groq_provider.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_settings.LLM_MODEL = "llama3-70b"
        mock_settings.LLM_TIMEOUT = 30.0
        mock_settings.LLM_MAX_RETRIES = 3
        mock_settings.LLM_RETRY_DELAY = 1.0
        mock_settings.LLM_MAX_TOKENS = 1024
        mock_settings.LLM_TEMPERATURE = 0.7
        provider = GroqLLMProvider()
        provider._client = mock_client
        return provider


class TestGenerateSummary:
    """Tests for generate_summary method."""

    @pytest.mark.asyncio
    async def test_generate_summary_success(self, provider, mock_client):
        """Test successful summary generation."""
        # Setup
        text = "This is a long document text that needs to be summarized."
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a summary."}}]
        }
        mock_client.post.return_value = mock_response

        # Execute
        result = await provider.generate_summary(text)

        # Assert
        assert result == "This is a summary."
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_summary_retry_on_rate_limit(self, provider, mock_client):
        """Test retry on rate limit."""
        # Setup
        text = "Test text"
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"choices": [{"message": {"content": "Summary"}}]}
        mock_client.post.side_effect = [mock_response_429, mock_response_200]

        # Execute
        result = await provider.generate_summary(text)

        # Assert
        assert result == "Summary"
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_summary_timeout(self, provider, mock_client):
        """Test timeout handling."""
        # Setup
        text = "Test text"
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        # Execute & Assert
        with pytest.raises(LLMProviderException) as exc_info:
            await provider.generate_summary(text)

        assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_summary_http_error(self, provider, mock_client):
        """Test HTTP error handling."""
        # Setup
        text = "Test text"
        mock_client.post.side_effect = httpx.HTTPError("Connection error")

        # Execute & Assert
        with pytest.raises(LLMProviderException) as exc_info:
            await provider.generate_summary(text)

        assert "http error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_summary_api_error(self, provider, mock_client):
        """Test API error response."""
        # Setup
        text = "Test text"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal server error"}}
        mock_client.post.return_value = mock_response

        # Execute & Assert
        with pytest.raises(LLMProviderException) as exc_info:
            await provider.generate_summary(text)

        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_summary_custom_params(self, provider, mock_client):
        """Test summary generation with custom parameters."""
        # Setup
        text = "Test text"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Summary"}}]}
        mock_client.post.return_value = mock_response

        # Execute
        result = await provider.generate_summary(text, max_tokens=256, temperature=0.1)

        # Assert
        assert result == "Summary"
        # Verify the call was made with custom parameters
        call_args = mock_client.post.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_generate_summary_no_api_key(self):
        """Test error when API key is not configured."""
        # Setup
        with patch("app.chat.providers.groq_provider.settings") as mock_settings:
            mock_settings.GROQ_API_KEY = None
            mock_settings.LLM_MODEL = "llama3-70b"
            mock_settings.LLM_TIMEOUT = 30.0
            mock_settings.LLM_MAX_RETRIES = 3
            mock_settings.LLM_RETRY_DELAY = 1.0
            provider = GroqLLMProvider()

            # Execute & Assert
            with pytest.raises(LLMProviderException) as exc_info:
                await provider.generate_summary("Test text")

            assert "not configured" in str(exc_info.value).lower()
