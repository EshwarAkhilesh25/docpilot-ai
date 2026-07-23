"""Search result model for vector similarity search."""

from dataclasses import dataclass


@dataclass
class SearchResult:
    """Result of a vector similarity search.

    This model represents a single search result containing the vector ID
    and its similarity score.
    """

    vector_id: str
    similarity_score: float

    def __repr__(self) -> str:
        return f"<SearchResult(vector_id={self.vector_id}, score={self.similarity_score:.4f})>"
