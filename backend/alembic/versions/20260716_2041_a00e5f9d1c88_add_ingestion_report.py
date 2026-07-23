"""add ingestion_report

Revision ID: a00e5f9d1c88
Revises: 003
Create Date: 2026-07-16 20:41:50.455901

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a00e5f9d1c88"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("processing_jobs", sa.Column("ingestion_report", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("processing_jobs", "ingestion_report")
