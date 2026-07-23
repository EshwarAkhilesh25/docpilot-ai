from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    """Mixin for adding soft delete functionality to SQLAlchemy models.

    This mixin provides soft delete capabilities, allowing records to be marked
    as deleted without actually removing them from the database. This is useful
    for data retention, audit trails, and recovery scenarios.

    The mixin is independent of BaseModel and can be composed with any
    SQLAlchemy model that needs soft delete capabilities.

    Attributes:
        deleted_at: Timestamp when the record was soft deleted. Null if the
                   record is active (not deleted).

    Methods:
        soft_delete(): Marks the record as deleted by setting deleted_at to now.
        restore(): Restores a deleted record by setting deleted_at to None.

    Properties:
        is_deleted: Returns True if the record has been soft deleted.

    Example:
        class MyModel(BaseModel, SoftDeleteMixin):
            __tablename__ = "my_table"
            name: Mapped[str] = mapped_column(String(255))

        # Usage
        model = MyModel(name="test")
        model.soft_delete()  # Marks as deleted
        model.is_deleted  # True
        model.restore()  # Restores the record
        model.is_deleted  # False
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    def soft_delete(self) -> None:
        """Mark the record as deleted by setting deleted_at to current timestamp."""
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restore a soft-deleted record by clearing the deleted_at timestamp."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if the record has been soft deleted.

        Returns:
            True if deleted_at is not None, False otherwise.
        """
        return self.deleted_at is not None
