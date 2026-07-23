"""Markdown Response Formatter."""

from app.chat.interfaces.response_formatter import ResponseFormatter


class MarkdownFormatter(ResponseFormatter):
    """Passes through the Markdown response from the LLM, potentially cleaning it."""

    def format(self, raw_response: str) -> str:
        """Format the response."""
        # Could strip out excessive newlines, ensure headers are spaced, etc.
        return raw_response.strip()
