"""Add merchant_id to products

Revision ID: b8d1e2f3a4c5
Revises: 9b39ab7bfb55
Create Date: 2026-09-05 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b8d1e2f3a4c5"
down_revision: str | Sequence[str] | None = "9b39ab7bfb55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add products.merchant_id with a backfill default for existing rows."""
    op.add_column(
        "products",
        sa.Column(
            "merchant_id",
            sa.BigInteger(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_index(
        "ix_products_merchant_id", "products", ["merchant_id"], unique=False
    )


def downgrade() -> None:
    """Drop the products.merchant_id column."""
    op.drop_index("ix_products_merchant_id", table_name="products")
    op.drop_column("products", "merchant_id")
