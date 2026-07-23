from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class FileMetadataMixin:
    """Mixin for file metadata fields in SQLAlchemy models.

    This mixin groups common file-related metadata fields into a reusable
    abstraction. It provides a clean way to organize file information across
    different models that need to track file storage details.

    The mixin preserves the existing database schema while providing a logical
    grouping of related fields for better code organization and maintainability.

    Attributes:
        original_filename: The original name of the file as uploaded by the user.
        stored_filename: The generated filename used for storage (e.g., UUID-based).
        mime_type: The MIME type of the file (e.g., 'application/pdf').
        file_size: The size of the file in bytes.
        storage_path: The path where the file is stored (e.g., S3 key or local path).
        checksum: Optional hash/checksum of the file for integrity verification.

    Example:
        class Document(BaseModel, FileMetadataMixin):
            __tablename__ = "documents"
            # Additional document-specific fields...
    """

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
