"""DOCX text extractor."""

import logging
from pathlib import Path

from docx import Document

from app.ingestion.exceptions import ExtractionFailedException
from app.ingestion.models import ExtractedText

logger = logging.getLogger(__name__)


class DOCXTextExtractor:
    """Extractor for DOCX files using python-docx.

    This class handles the low-level text extraction from DOCX files,
    maintaining page (or paragraph) boundaries where possible. Since DOCX doesn't
    have strict page concepts like PDF, we extract text and optionally track paragraphs.
    """

    async def extract_text(self, file_path: Path) -> ExtractedText:
        """Extract text from a DOCX file.

        Args:
            file_path: Path to the DOCX file.

        Returns:
            ExtractedText containing the raw text and metadata.

        Raises:
            ExtractionFailedException: If extraction fails.
        """
        try:
            pass

            # Using python-docx to read the document
            doc = Document(str(file_path))

            full_text = []

            # Since DOCX is reflowable, we don't have true pages.
            # We treat the entire document as page 1.
            # For simplicity, we just concatenate paragraphs.
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)

            raw_text = "\n\n".join(full_text)

            # Create a single "page" metadata entry for chunking strategies that expect pages
            pages_metadata = [
                {
                    "page_number": 1,
                    "text": raw_text,
                    "start_character": 0,
                    "end_character": len(raw_text),
                }
            ]

            metadata = {
                "source": str(file_path),
                "paragraph_count": len(full_text),
                "pages": pages_metadata,
            }

            pass

            return ExtractedText(text=raw_text, metadata=metadata)

        except Exception as e:
            pass
            raise ExtractionFailedException(f"DOCX extraction failed: {e}")
