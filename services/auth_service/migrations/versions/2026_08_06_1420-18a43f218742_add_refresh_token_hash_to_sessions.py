"""Add refresh_token_hash to sessions

Revision ID: 18a43f218742
Revises: aaf016332f65
Create Date: 2026-08-06 14:20:05.879205

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18a43f218742"
down_revision: str | Sequence[str] | None = "aaf016332f65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sessions", sa.Column("refresh_token_hash", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sessions", "refresh_token_hash")
