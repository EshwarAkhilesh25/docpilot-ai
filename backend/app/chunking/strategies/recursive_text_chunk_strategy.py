"""Recursive text chunking strategy."""

import logging
import re
from typing import Any

from app.chunking.interfaces.chunk_strategy import ChunkStrategy
from app.chunking.models.chunk import Chunk

logger = logging.getLogger(__name__)


class RecursiveTextChunkStrategy(ChunkStrategy):
    """Recursive text chunking strategy.

    This strategy splits text into chunks while trying to preserve:
    1. Paragraph boundaries (preferred)
    2. Sentence boundaries (fallback)
    3. Character boundaries (last resort)

    Chunks have overlap to ensure context is preserved across boundaries.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        pages: list[dict[str, Any]] | None = None,
    ):
        """Initialize the recursive text chunking strategy.

        Args:
            chunk_size: Maximum characters per chunk (default: 1000).
            chunk_overlap: Number of characters to overlap between chunks (default: 200).
            pages: List of page data with page numbers and text for page boundary tracking.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pages = pages or []

    def chunk(self, text: str) -> list[Chunk]:
        """Split text into chunks.

        Args:
            text: The text to chunk.

        Returns:
            List of Chunk objects containing the chunked text and metadata.
        """
        if not text:
            return []

        chunks = []
        seen_chunks = set()
        current_position = 0
        chunk_index = 0

        while current_position < len(text):
            # Calculate the end position for this chunk
            end_position = min(current_position + self.chunk_size, len(text))

            # Try to find a good split point
            split_position = self._find_split_position(text, current_position, end_position)

            # Extract the chunk text
            chunk_text = text[current_position:split_position].strip()

            if chunk_text and chunk_text not in seen_chunks:
                # Determine page number for this chunk
                page_number = self._get_page_number(current_position, split_position)

                chunk = Chunk(
                    chunk_index=chunk_index,
                    text=chunk_text,
                    start_character=current_position,
                    end_character=split_position,
                    page_number=page_number,
                )
                chunks.append(chunk)
                seen_chunks.add(chunk_text)
                chunk_index += 1

            # Move to next position with overlap
            if split_position >= len(text):
                break

            next_position = split_position - self.chunk_overlap
            if next_position <= current_position:
                next_position = current_position + 1

            current_position = next_position

        # Fallback: if we somehow produced zero chunks but had text, force one chunk
        if not chunks and text.strip():
            fallback_text = text[: self.chunk_size].strip()
            if fallback_text:
                chunks.append(
                    Chunk(
                        chunk_index=0,
                        text=fallback_text,
                        start_character=0,
                        end_character=len(fallback_text),
                        page_number=self._get_page_number(0, len(fallback_text)),
                    )
                )

        # Detailed logging for RAG debugging
        pass

        return chunks

    def _find_split_position(self, text: str, start: int, end: int) -> int:
        """Find the best position to split text.

        Tries to split at paragraph boundaries first, then sentences,
        then falls back to character splitting.

        Args:
            text: The full text.
            start: Start position for the chunk.
            end: End position for the chunk.

        Returns:
            The optimal split position.
        """
        # If we're at the end, return end
        if end >= len(text):
            return end

        # Search backwards from end for paragraph boundary
        paragraph_split = self._find_paragraph_split(text, start, end)
        if paragraph_split > start:
            return paragraph_split

        # Search backwards for sentence boundary
        sentence_split = self._find_sentence_split(text, start, end)
        if sentence_split > start:
            return sentence_split

        # Fall back to character split at end
        return end

    def _find_paragraph_split(self, text: str, start: int, end: int) -> int:
        """Find a paragraph boundary within the chunk range.

        Args:
            text: The full text.
            start: Start position for the chunk.
            end: End position for the chunk.

        Returns:
            Position of paragraph boundary, or start if not found.
        """
        # Look for double newlines (paragraph separator)
        search_range = text[start:end]
        last_paragraph = search_range.rfind("\n\n")

        if last_paragraph != -1:
            return start + last_paragraph + 2  # +2 to include the newlines

        # Look for single newline
        last_newline = search_range.rfind("\n")
        if last_newline != -1:
            return start + last_newline + 1

        return start

    def _find_sentence_split(self, text: str, start: int, end: int) -> int:
        """Find a sentence boundary within the chunk range.

        Args:
            text: The full text.
            start: Start position for the chunk.
            end: End position for the chunk.

        Returns:
            Position of sentence boundary, or start if not found.
        """
        # Common sentence endings: . ! ? followed by space or newline
        search_range = text[start:end]

        # Pattern: sentence ending followed by space or newline
        pattern = r"[.!?](?:\s|\n)"
        matches = list(re.finditer(pattern, search_range))

        if matches:
            last_match = matches[-1]
            return start + last_match.end()

        return start

    def _get_page_number(self, start: int, end: int) -> int | None:
        """Determine the page number for a chunk based on character positions.

        Args:
            start: Start character position.
            end: End character position.

        Returns:
            Page number if available, None otherwise.
        """
        if not self.pages:
            return None

        # Calculate cumulative character positions for each page
        cumulative_chars = 0
        for page_data in self.pages:
            page_text = page_data.get("text", "")
            page_num = page_data.get("page")
            cumulative_chars += len(page_text)

            # If the chunk starts within this page's range
            if start < cumulative_chars:
                return page_num

        return None
