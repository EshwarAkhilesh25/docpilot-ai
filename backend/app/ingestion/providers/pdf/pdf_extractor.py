"""PDF text extractor using PyMuPDF (fitz)."""

import logging
from typing import Any

import fitz  # PyMuPDF

from app.ingestion.exceptions import ExtractionFailedException

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """Extract text from PDF files using PyMuPDF.

    This extractor preserves page boundaries internally for future chunking
    and citation capabilities, while also providing combined text for storage.
    """

    def extract(self, file_path: str) -> dict[str, Any]:
        """Extract text and metadata from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Dictionary containing:
            - pages: List of dicts with page number and text
            - raw_text: Combined text from all pages
            - page_count: Total number of pages
            - character_count: Total character count
            - metadata: PDF metadata

        Raises:
            ExtractionFailedException: If extraction fails.
        """
        try:
            doc = fitz.open(file_path)

            # Detailed logging for debugging
            pass

            if doc.page_count == 0:
                pass
                doc.close()
                return {
                    "pages": [],
                    "raw_text": "",
                    "page_count": 0,
                    "character_count": 0,
                    "metadata": {},
                }

            pages_data = []
            raw_text_parts = []
            total_chars = 0
            ocr_used = False

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                # Check text quality (valid if > 30% of non-whitespace characters are alphabetic)
                is_valid = False
                if text and text.strip():
                    alpha_count = sum(1 for c in text if c.isalpha())
                    non_space = sum(1 for c in text if not c.isspace())
                    if non_space > 0 and (alpha_count / non_space) > 0.3:
                        is_valid = True

                # Log page extraction details
                pass

                # If text extraction returns empty or garbage, try OCR for image-based PDFs
                if not is_valid:
                    pass
                    ocr_used = True
                    text = self._extract_text_with_ocr(page)
                    pass

                # Skip empty pages
                if not text.strip():
                    continue

                page_data = {
                    "page": page_num + 1,  # 1-based page numbering
                    "text": text,
                }
                pages_data.append(page_data)
                raw_text_parts.append(text)
                total_chars += len(text)

            # Combine text with page separators for storage
            raw_text = "\n\n".join(raw_text_parts)

            # Extract PDF metadata
            metadata = self._extract_metadata(doc)

            doc.close()

            # Fail fast if document is effectively empty
            if total_chars < 50 and not raw_text.strip():
                raise ExtractionFailedException(
                    "Extracted text is empty or too short to be useful."
                )

            # Detailed logging for RAG debugging
            pass

            pass

            return {
                "pages": pages_data,
                "raw_text": raw_text,
                "page_count": len(pages_data),
                "character_count": total_chars,
                "metadata": metadata,
                "ocr_used": ocr_used,
            }

        except Exception as e:
            pass
            raise ExtractionFailedException(f"PDF extraction failed: {e}")

    def _extract_metadata(self, doc: fitz.Document) -> dict[str, Any]:
        """Extract metadata from PDF document.

        Args:
            doc: PyMuPDF Document object.

        Returns:
            Dictionary of PDF metadata.
        """
        metadata = {}

        try:
            # Standard PDF metadata
            pdf_metadata = doc.metadata
            if pdf_metadata:
                metadata["title"] = pdf_metadata.get("title")
                metadata["author"] = pdf_metadata.get("author")
                metadata["subject"] = pdf_metadata.get("subject")
                metadata["keywords"] = pdf_metadata.get("keywords")
                metadata["creator"] = pdf_metadata.get("creator")
                metadata["producer"] = pdf_metadata.get("producer")
                metadata["creation_date"] = pdf_metadata.get("creationDate")
                metadata["modification_date"] = pdf_metadata.get("modDate")

            # Page dimensions
            if doc.page_count > 0:
                first_page = doc[0]
                metadata["page_width"] = first_page.rect.width
                metadata["page_height"] = first_page.rect.height

        except Exception:
            pass

        return metadata

    def _extract_text_with_ocr(self, page) -> str:
        """Extract text from a PDF page using OCR for image-based PDFs.

        Args:
            page: PyMuPDF Page object.

        Returns:
            Extracted text string.
        """
        # Try using pytesseract if available
        try:
            import io

            # Configure tesseract path for Windows
            import os

            import pytesseract
            from PIL import Image

            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                pass

            # Get page as image at 300 DPI (72 default -> 300/72 = 4.16)
            matrix = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=matrix)
            img_data = pix.tobytes("png")

            image = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(image)
            if text.strip():
                pass
                return text
            else:
                pass
        except ImportError:
            pass
        except Exception:
            pass

        return ""
