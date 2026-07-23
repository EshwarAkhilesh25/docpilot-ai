"""Exceptions for embedding generation."""


class EmbeddingGenerationException(Exception):
    """Exception raised when embedding generation fails.

    This exception is raised when there is an error generating embeddings
    for text, such as model loading failures or inference errors.
    """

    pass
