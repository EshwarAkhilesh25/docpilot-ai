from abc import ABC, abstractmethod

from app.ingestion.models import ExtractionResult


class TextNormalizer(ABC):
    """Abstract interface for text normalization.

    A TextNormalizer is responsible for normalizing extracted text
    before downstream processing. This can include whitespace cleanup,
    unicode normalization, newline normalization, etc.
    """

    @abstractmethod
    def normalize(self, extracted_text: ExtractionResult) -> ExtractionResult:
        """Normalize extracted text.

        Args:
            extracted_text: The extracted text to normalize.

        Returns:
            Normalized ExtractionResult.
        """
        pass
