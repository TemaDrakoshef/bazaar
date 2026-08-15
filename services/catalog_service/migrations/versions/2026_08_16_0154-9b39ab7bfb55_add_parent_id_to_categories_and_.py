"""Add parent_id to categories and backfill from ltree path

Revision ID: 9b39ab7bfb55
Revises: d3a8bd4ec0f9
Create Date: 2026-08-16 01:54:39.315469

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b39ab7bfb55"
down_revision: str | Sequence[str] | None = "d3a8bd4ec0f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("categories", sa.Column("parent_id", sa.BigInteger(), nullable=True))

    op.execute(
        """
        UPDATE categories
        SET parent_id = CAST(
            split_part(ltree2text(path), '.', nlevel(path) - 1) AS BIGINT
        )
        WHERE nlevel(path) > 1
        """
    )

    op.create_index(
        op.f("ix_categories_parent_id"), "categories", ["parent_id"], unique=False
    )
    op.create_foreign_key(
        "fk_categories_parent_id",
        "categories",
        "categories",
        ["parent_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_categories_parent_id", "categories", type_="foreignkey")
    op.drop_index(op.f("ix_categories_parent_id"), table_name="categories")
    op.drop_column("categories", "parent_id")
