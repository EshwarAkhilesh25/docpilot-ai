"""Embedding model."""

from dataclasses import dataclass
from uuid import UUID

import numpy as np


@dataclass
class Embedding:
    """Represents a text embedding vector with metadata.

    This model stores the embedding vector along with its associated
    identifier for tracking in the vector database.
    """

    vector_id: UUID
    vector: np.ndarray
    text: str | None = None

    def __repr__(self) -> str:
        return f"<Embedding(vector_id={self.vector_id}, dimension={self.vector.shape[0]})>"
