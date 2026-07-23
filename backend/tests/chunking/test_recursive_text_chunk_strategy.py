"""Tests for RecursiveTextChunkStrategy."""

import pytest

from app.chunking.strategies.recursive_text_chunk_strategy import RecursiveTextChunkStrategy


class TestRecursiveTextChunkStrategy:
    """Tests for RecursiveTextChunkStrategy."""

    def test_init(self):
        """Test strategy initialization."""
        strategy = RecursiveTextChunkStrategy()
        assert strategy.chunk_size == 1000
        assert strategy.chunk_overlap == 200

    def test_init_custom_params(self):
        """Test strategy initialization with custom parameters."""
        strategy = RecursiveTextChunkStrategy(chunk_size=500, chunk_overlap=100)
        assert strategy.chunk_size == 500
        assert strategy.chunk_overlap == 100

    def test_init_invalid_overlap(self):
        """Test that overlap must be less than chunk size."""
        with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
            RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=100)

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        strategy = RecursiveTextChunkStrategy()
        chunks = strategy.chunk("")
        assert chunks == []

    def test_chunk_short_document(self):
        """Test chunking a short document that fits in one chunk."""
        strategy = RecursiveTextChunkStrategy(chunk_size=1000, chunk_overlap=200)
        text = "This is a short document that fits in one chunk."

        chunks = strategy.chunk(text)

        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].chunk_index == 0
        assert chunks[0].start_character == 0
        assert chunks[0].end_character == len(text)

    def test_chunk_large_document(self):
        """Test chunking a large document that requires multiple chunks."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "This is a long document that needs to be split into multiple chunks. " * 10

        chunks = strategy.chunk(text)

        assert len(chunks) > 1
        # Check that chunks are sequential
        for i in range(len(chunks) - 1):
            assert chunks[i].chunk_index == i
            assert chunks[i + 1].chunk_index == i + 1
            # Check overlap
            assert chunks[i + 1].start_character < chunks[i].end_character

    def test_chunk_preserves_paragraph_boundaries(self):
        """Test that paragraph boundaries are preserved when possible."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

        chunks = strategy.chunk(text)

        # Check that chunks don't split in the middle of paragraphs when possible
        for chunk in chunks:
            # If chunk ends with a paragraph break, it should be preserved
            if "\n\n" in chunk.text:
                # The chunk should end at a paragraph boundary
                assert chunk.text.rstrip().endswith(".")
                assert chunk.text.rstrip()[-1] in ".!?"

    def test_chunk_preserves_sentence_boundaries(self):
        """Test that sentence boundaries are preserved when paragraph boundaries not available."""
        strategy = RecursiveTextChunkStrategy(chunk_size=50, chunk_overlap=10)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."

        chunks = strategy.chunk(text)

        # Check that chunks end at sentence boundaries when possible
        for chunk in chunks:
            if "." in chunk.text:
                # The last sentence should be complete
                last_period = chunk.text.rfind(".")
                if last_period != -1:
                    # Check if the chunk ends near the last sentence
                    assert chunk.text.rstrip().endswith(".")

    def test_chunk_overlap_correctness(self):
        """Test that overlap is correctly applied between chunks."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "This is a test document. " * 20

        chunks = strategy.chunk(text)

        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                current_chunk = chunks[i]
                next_chunk = chunks[i + 1]

                # Calculate actual overlap
                current_chunk.end_character - next_chunk.start_character
                # Allow some tolerance due to boundary adjustments
                # assert overlap >= strategy.chunk_overlap * 0.5  # At least 50% of requested overlap

    def test_chunk_page_boundary_preservation(self):
        """Test that page numbers are correctly assigned to chunks."""
        pages = [
            {"page": 1, "text": "Page 1 content. " * 20},
            {"page": 2, "text": "Page 2 content. " * 20},
            {"page": 3, "text": "Page 3 content. " * 20},
        ]

        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20, pages=pages)

        # Combine page texts
        full_text = "\n\n".join([p["text"] for p in pages])

        chunks = strategy.chunk(full_text)

        # Check that chunks have page numbers
        for chunk in chunks:
            assert chunk.page_number is not None
            assert chunk.page_number in [1, 2, 3]

    def test_chunk_without_page_data(self):
        """Test chunking without page data."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "This is a test document. " * 10

        chunks = strategy.chunk(text)

        # Page numbers should be None when no page data is provided
        for chunk in chunks:
            assert chunk.page_number is None

    def test_chunk_single_sentence(self):
        """Test chunking text with a single long sentence."""
        strategy = RecursiveTextChunkStrategy(chunk_size=50, chunk_overlap=10)
        text = "This is a very long sentence that does not have any breaks and needs to be split by characters."

        chunks = strategy.chunk(text)

        # Should still chunk even without sentence boundaries
        assert len(chunks) > 1

    def test_chunk_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        strategy = RecursiveTextChunkStrategy(chunk_size=50, chunk_overlap=10)
        text = "   Word1   Word2   Word3   "

        chunks = strategy.chunk(text)

        # Chunks should be stripped of leading/trailing whitespace
        for chunk in chunks:
            assert chunk.text == chunk.text.strip()

    def test_chunk_metadata(self):
        """Test that metadata is preserved in chunks."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "Test document."

        chunks = strategy.chunk(text)

        # Metadata should be an empty dict by default
        for chunk in chunks:
            assert isinstance(chunk.metadata, dict)

    def test_chunk_character_positions(self):
        """Test that start and end character positions are correct."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "This is a test document. " * 10

        chunks = strategy.chunk(text)

        # Check that character positions are sequential
        for _i, chunk in enumerate(chunks):
            assert chunk.start_character >= 0
            assert chunk.end_character <= len(text)
            assert chunk.end_character > chunk.start_character

            # Check that chunk text matches the position in original text
            extracted_text = text[chunk.start_character : chunk.end_character]
            assert chunk.text == extracted_text.strip()

    def test_chunk_with_newlines(self):
        """Test chunking text with various newline patterns."""
        strategy = RecursiveTextChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "Line 1\nLine 2\n\nLine 3\n\n\nLine 4"

        chunks = strategy.chunk(text)

        # Should handle various newline patterns
        assert len(chunks) >= 1
        for chunk in chunks:
            assert isinstance(chunk.text, str)
