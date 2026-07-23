from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    """Mixin for adding audit fields to SQLAlchemy models.

    This mixin provides tracking of who created and last modified a record.
    It is designed for future administrative and multi-user features where
    tracking the user responsible for changes is required.

    The mixin is independent of BaseModel and can be composed with any
    SQLAlchemy model that needs audit capabilities.

    Attributes:
        created_by: UUID of the user who created the record. Nullable to support
                   system-generated records or migration scenarios.
        updated_by: UUID of the user who last modified the record. Nullable to
                   support system updates or migration scenarios.

    Example:
        class MyModel(BaseModel, AuditMixin):
            __tablename__ = "my_table"
            name: Mapped[str] = mapped_column(String(255))
    """

    created_by: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    updated_by: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
