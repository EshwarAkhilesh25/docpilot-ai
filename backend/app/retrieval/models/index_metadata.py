"""Index metadata model for vector index tracking."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IndexMetadata:
    """Metadata about a vector index.

    This model stores metadata about the vector index including the embedding model,
    dimension, version, and creation timestamp. This is used to validate that
    the loaded index is compatible with the current configuration.
    """

    embedding_model: str
    dimension: int
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    vector_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "embedding_model": self.embedding_model,
            "dimension": self.dimension,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "vector_count": self.vector_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IndexMetadata":
        """Create from dictionary."""
        return cls(
            embedding_model=data["embedding_model"],
            dimension=data["dimension"],
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data["created_at"]),
            vector_count=data.get("vector_count", 0),
        )
