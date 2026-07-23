"""JSON Response Formatter."""

import json
import re

from app.chat.interfaces.response_formatter import ResponseFormatter


class JSONFormatter(ResponseFormatter):
    """Ensures the response is valid JSON, stripping markdown code blocks if necessary."""

    def format(self, raw_response: str) -> str:
        """Format the response as JSON."""
        # Try to extract JSON from markdown block
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = raw_response

        json_str = json_str.strip()

        try:
            # Validate it parses
            parsed = json.loads(json_str)
            # Re-serialize to string to ensure consistent format
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # If it fails, return the raw string and let the frontend handle the error gracefully
            return raw_response
