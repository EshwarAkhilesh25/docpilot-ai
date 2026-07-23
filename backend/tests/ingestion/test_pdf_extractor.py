"""Tests for PDF text extractor."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.providers.pdf.pdf_extractor import PDFTextExtractor


class TestPDFTextExtractor:
    """Tests for PDFTextExtractor."""

    def test_init(self):
        """Test extractor initialization."""
        extractor = PDFTextExtractor()
        assert extractor is not None

    def test_extract_single_page_pdf(self):
        """Test extracting text from a single page PDF."""
        PDFTextExtractor()

        # This test requires a sample PDF file
        # For now, we'll skip if no test PDF is available
        pytest.skip("Requires sample PDF file")

    def test_extract_multi_page_pdf(self):
        """Test extracting text from a multi-page PDF."""
        PDFTextExtractor()

        # This test requires a sample multi-page PDF file
        pytest.skip("Requires sample multi-page PDF file")

    def test_extract_empty_page_pdf(self):
        """Test extracting text from a PDF with empty pages."""
        PDFTextExtractor()

        # This test requires a sample PDF with empty pages
        pytest.skip("Requires sample PDF with empty pages")

    def test_extract_corrupted_pdf(self):
        """Test extracting text from a corrupted PDF."""
        extractor = PDFTextExtractor()

        with TemporaryDirectory() as temp_dir:
            # Create a corrupted file
            corrupted_file = Path(temp_dir) / "corrupted.pdf"
            corrupted_file.write_text("This is not a valid PDF")

            with pytest.raises(ExtractionFailedException):
                extractor.extract(str(corrupted_file))

    def test_extract_nonexistent_file(self):
        """Test extracting text from a non-existent file."""
        extractor = PDFTextExtractor()

        with pytest.raises(ExtractionFailedException):
            extractor.extract("/nonexistent/file.pdf")

    def test_extract_preserves_page_boundaries(self):
        """Test that page boundaries are preserved in extraction."""
        PDFTextExtractor()

        # This test requires a sample PDF file
        pytest.skip("Requires sample PDF file")

    def test_extract_metadata(self):
        """Test that PDF metadata is extracted."""
        PDFTextExtractor()

        # This test requires a sample PDF with metadata
        pytest.skip("Requires sample PDF with metadata")
