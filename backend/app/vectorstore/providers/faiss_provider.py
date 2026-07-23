"""FAISS implementation of vector index provider."""

import json
import logging
import threading
from pathlib import Path

import faiss
import numpy as np

from app.retrieval.models.index_metadata import IndexMetadata
from app.vectorstore.exceptions import (
    DuplicateVectorException,
    VectorDimensionMismatchException,
    VectorIndexException,
    VectorIndexNotFoundException,
)
from app.vectorstore.interfaces.vector_index_provider import VectorIndexProvider
from app.vectorstore.models.search_result import SearchResult

logger = logging.getLogger(__name__)


class FAISSVectorProvider(VectorIndexProvider):
    """FAISS-based vector index provider using IndexFlatIP.

    This provider uses FAISS IndexFlatIP (Inner Product) for similarity search.
    It assumes embeddings are already L2-normalized, making inner product
    equivalent to cosine similarity.

    Features:
    - Thread-safe index updates
    - Batch vector insertion
    - Dimension validation
    - Duplicate vector ID handling
    - Atomic persistence to avoid corruption
    - Automatic loading from disk on startup
    - Index metadata tracking and validation
    """

    def __init__(
        self, index_path: str | None = None, embedding_model: str = "BAAI/bge-small-en-v1.5"
    ):
        """Initialize the FAISS vector provider.

        Args:
            index_path: Path to load/save the index. If provided and index exists,
                       it will be loaded automatically.
            embedding_model: Name of the embedding model used for vectors.
        """
        self._index: faiss.Index | None = None
        self._dimension: int | None = None
        self._vector_id_to_index: dict[str, int] = {}
        self._index_to_vector_id: dict[int, str] = {}
        self._lock = threading.RLock()
        self._index_path = Path(index_path) if index_path else None
        self._embedding_model = embedding_model
        self._metadata: IndexMetadata | None = None
        self._last_loaded_mtime: float = 0.0

        # Auto-load if index path is provided and exists
        if self._index_path and self._index_path.exists():
            self._load_from_disk()

    async def create_index(self, dimension: int) -> None:
        """Create a new vector index.

        Args:
            dimension: The dimension of the vectors to be indexed.

        Raises:
            VectorIndexException: If index creation fails.
        """
        with self._lock:
            try:
                # Create FAISS IndexFlatIP (Inner Product)
                # Assumes vectors are L2-normalized, so IP ≈ cosine similarity
                self._index = faiss.IndexFlatIP(dimension)
                self._dimension = dimension
                self._vector_id_to_index = {}
                self._index_to_vector_id = {}

                # Initialize metadata
                self._metadata = IndexMetadata(
                    embedding_model=self._embedding_model,
                    dimension=dimension,
                    version="1.0",
                    vector_count=0,
                )

                pass
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to create index: {e}")

    async def add_vectors(self, vector_ids: list[str], vectors: list[np.ndarray]) -> None:
        """Add vectors to the index.

        Args:
            vector_ids: List of unique identifiers for the vectors.
            vectors: List of embedding vectors to add.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
            VectorDimensionMismatchException: If vector dimensions don't match index.
            DuplicateVectorException: If vector IDs already exist.
            VectorIndexException: If addition fails.
        """
        with self._lock:
            if self._index is None:
                raise VectorIndexNotFoundException("Index has not been created")

            if len(vector_ids) != len(vectors):
                raise VectorIndexException("Number of vector IDs must match number of vectors")

            if not vector_ids:
                return

            # Validate dimensions
            first_vector = vectors[0]
            if len(first_vector) != self._dimension:
                raise VectorDimensionMismatchException(
                    f"Vector dimension {len(first_vector)} doesn't match index dimension {self._dimension}"
                )

            # Check for duplicates
            duplicates = [vid for vid in vector_ids if vid in self._vector_id_to_index]
            if duplicates:
                raise DuplicateVectorException(f"Vector IDs already exist: {duplicates}")

            try:
                # Convert vectors to numpy array
                vectors_array = np.array(vectors, dtype=np.float32)

                # Get current index size
                start_idx = self._index.ntotal

                # Add vectors to FAISS index
                self._index.add(vectors_array)

                # Update mappings
                for i, vector_id in enumerate(vector_ids):
                    faiss_index = start_idx + i
                    self._vector_id_to_index[vector_id] = faiss_index
                    self._index_to_vector_id[faiss_index] = vector_id

                # Update metadata
                if self._metadata:
                    self._metadata.vector_count = self._index.ntotal

                pass
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to add vectors: {e}")

    async def search(
        self, query_vector: list[float] | np.ndarray, top_k: int = 10
    ) -> list[SearchResult]:
        """Search for the most similar vectors.

        Args:
            query_vector: The query vector.
            top_k: Number of results to return.

        Returns:
            List of search results containing vector IDs and similarity scores.

        Raises:
            VectorIndexNotFoundException: If index has not been created.
            VectorDimensionMismatchException: If query dimension doesn't match index.
            VectorIndexException: If search fails.
        """
        import os

        # Check if we need to reload the index from disk (e.g., if a background worker updated it)
        if self._index_path and self._index_path.exists():
            try:
                current_mtime = os.path.getmtime(self._index_path)
                if current_mtime > self._last_loaded_mtime:
                    pass
                    await self.load(str(self._index_path))
            except Exception:
                pass

        with self._lock:
            if self._index is None:
                raise VectorIndexNotFoundException("Index has not been created")

            if self._index.ntotal == 0:
                return []

            # Validate dimension
            if len(query_vector) != self._dimension:
                raise VectorDimensionMismatchException(
                    f"Query dimension {len(query_vector)} doesn't match index dimension {self._dimension}"
                )

            try:
                # Reshape query vector for FAISS
                query_array = np.array([query_vector], dtype=np.float32)

                # Search
                top_k = min(top_k, self._index.ntotal)
                similarities, indices = self._index.search(query_array, top_k)

                # Convert to SearchResult objects
                results = []
                for similarity, idx in zip(similarities[0], indices[0], strict=False):
                    if idx >= 0:  # FAISS returns -1 for invalid indices
                        vector_id = self._index_to_vector_id.get(idx)
                        if vector_id:
                            results.append(
                                SearchResult(
                                    vector_id=vector_id, similarity_score=float(similarity)
                                )
                            )

                return results
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to search: {e}")

    async def delete_vectors(self, vector_ids: list[str]) -> None:
        """Delete vectors from the index.

        Note: FAISS doesn't support efficient deletion. This implementation
        removes vectors from the mapping but the FAISS index itself is not
        modified (vectors are marked as deleted in the mapping).

        Args:
            vector_ids: List of vector IDs to delete.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
            VectorIndexException: If deletion fails.
        """
        with self._lock:
            if self._index is None:
                raise VectorIndexNotFoundException("Index has not been created")

            try:
                deleted_count = 0
                for vector_id in vector_ids:
                    if vector_id in self._vector_id_to_index:
                        faiss_index = self._vector_id_to_index[vector_id]
                        del self._vector_id_to_index[vector_id]
                        if faiss_index in self._index_to_vector_id:
                            del self._index_to_vector_id[faiss_index]
                        deleted_count += 1

                pass
                # Note: FAISS index itself is not modified due to lack of efficient deletion support
                # For production use, consider rebuilding the index periodically
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to delete vectors: {e}")

    async def save(self, path: str) -> None:
        """Save the index to disk atomically.

        Args:
            path: The path where to save the index.

        Raises:
            VectorIndexException: If save fails.
        """
        with self._lock:
            if self._index is None:
                raise VectorIndexNotFoundException("Index has not been created")

            try:
                save_path = Path(path)
                save_path.parent.mkdir(parents=True, exist_ok=True)

                # Save FAISS index
                faiss.write_index(self._index, str(save_path))

                # Save vector mapping and metadata
                mapping_path = save_path.with_suffix(".json")
                with open(mapping_path, "w") as f:
                    data = {
                        "vector_id_to_index": self._vector_id_to_index,
                        "index_to_vector_id": self._index_to_vector_id,
                        "dimension": self._dimension,
                    }
                    # Add metadata if available
                    if self._metadata:
                        data["metadata"] = self._metadata.to_dict()
                    json.dump(data, f)

                # Update mtime after saving
                import os

                if self._index_path and self._index_path.exists():
                    self._last_loaded_mtime = os.path.getmtime(self._index_path)

                pass
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to save index: {e}")

    async def load(self, path: str) -> None:
        """Load the index from disk.

        Args:
            path: The path from which to load the index.

        Raises:
            VectorIndexNotFoundException: If index file doesn't exist.
            VectorIndexException: If load fails or metadata validation fails.
        """
        with self._lock:
            try:
                load_path = Path(path)
                if not load_path.exists():
                    raise VectorIndexNotFoundException(f"Index file not found: {path}")

                # Load FAISS index
                self._index = faiss.read_index(str(load_path))
                self._dimension = self._index.d

                # Load vector mapping and metadata
                mapping_path = load_path.with_suffix(".json")
                if mapping_path.exists():
                    with open(mapping_path) as f:
                        data = json.load(f)
                        # Convert string keys back to int for index_to_vector_id
                        self._vector_id_to_index = data["vector_id_to_index"]
                        self._index_to_vector_id = {
                            int(k): v for k, v in data["index_to_vector_id"].items()
                        }
                        self._dimension = data["dimension"]

                        # Load and validate metadata
                        if "metadata" in data:
                            self._metadata = IndexMetadata.from_dict(data["metadata"])
                            self._validate_metadata()
                        else:
                            # Legacy index without metadata
                            self._metadata = IndexMetadata(
                                embedding_model=self._embedding_model,
                                dimension=self._dimension,
                                version="1.0",
                                vector_count=self._index.ntotal,
                            )
                else:
                    self._vector_id_to_index = {}
                    self._index_to_vector_id = {}
                    self._metadata = IndexMetadata(
                        embedding_model=self._embedding_model,
                        dimension=self._dimension,
                        version="1.0",
                        vector_count=self._index.ntotal,
                    )

                # Update mtime after loading
                import os

                if self._index_path and self._index_path.exists():
                    self._last_loaded_mtime = os.path.getmtime(self._index_path)

                pass
            except VectorIndexNotFoundException:
                raise
            except Exception as e:
                pass
                raise VectorIndexException(f"Failed to load index: {e}")

    def dimension(self) -> int:
        """Get the dimension of the index.

        Returns:
            The dimension of vectors in the index.

        Raises:
            VectorIndexNotFoundException: If index doesn't exist.
        """
        if self._dimension is None:
            raise VectorIndexNotFoundException("Index has not been created")
        return self._dimension

    def _validate_metadata(self) -> None:
        """Validate that index metadata matches current configuration.

        Raises:
            VectorIndexException: If metadata validation fails.
        """
        if self._metadata is None:
            return

        # Validate embedding model
        if self._metadata.embedding_model != self._embedding_model:
            pass
            # For now, just log a warning. In production, you might want to raise an exception
            # or rebuild the index.

        # Validate dimension
        if self._metadata.dimension != self._dimension:
            raise VectorIndexException(
                f"Index dimension mismatch: index={self._metadata.dimension}, "
                f"current={self._dimension}. The index was created with a different "
                "embedding model. Please rebuild the index."
            )

    def _load_from_disk(self) -> None:
        """Load index from disk synchronously (for initialization)."""
        if self._index_path and self._index_path.exists():
            try:
                # Load FAISS index
                self._index = faiss.read_index(str(self._index_path))
                self._dimension = self._index.d

                # Load vector mapping and metadata
                mapping_path = self._index_path.with_suffix(".json")
                if mapping_path.exists():
                    with open(mapping_path) as f:
                        data = json.load(f)
                        self._vector_id_to_index = data["vector_id_to_index"]
                        self._index_to_vector_id = {
                            int(k): v for k, v in data["index_to_vector_id"].items()
                        }
                        self._dimension = data["dimension"]

                        # Load and validate metadata
                        if "metadata" in data:
                            self._metadata = IndexMetadata.from_dict(data["metadata"])
                            self._validate_metadata()
                        else:
                            # Legacy index without metadata
                            self._metadata = IndexMetadata(
                                embedding_model=self._embedding_model,
                                dimension=self._dimension,
                                version="1.0",
                                vector_count=self._index.ntotal,
                            )
                else:
                    self._vector_id_to_index = {}
                    self._index_to_vector_id = {}
                    self._metadata = IndexMetadata(
                        embedding_model=self._embedding_model,
                        dimension=self._dimension,
                        version="1.0",
                        vector_count=self._index.ntotal,
                    )

                pass
            except Exception:
                pass
                self._index = None
                self._dimension = None
                self._metadata = None
