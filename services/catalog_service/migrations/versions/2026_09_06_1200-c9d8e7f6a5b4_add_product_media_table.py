"""Add product_media table

Revision ID: c9d8e7f6a5b4
Revises: b8d1e2f3a4c5
Create Date: 2026-09-06 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c9d8e7f6a5b4"
down_revision: str | Sequence[str] | None = "b8d1e2f3a4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the product_media table with its indexes."""
    op.create_table(
        "product_media",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "media_type",
            sa.Enum("IMAGE", "VIDEO", name="media_type_enum"),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_media_product_id"),
        "product_media",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        "ix_product_media_product_position",
        "product_media",
        ["product_id", "position"],
        unique=False,
    )
    op.create_index(
        "uq_product_single_video",
        "product_media",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("media_type = 'VIDEO'"),
    )


def downgrade() -> None:
    """Drop the product_media table."""
    op.drop_index("uq_product_single_video", table_name="product_media")
    op.drop_index("ix_product_media_product_position", table_name="product_media")
    op.drop_index(op.f("ix_product_media_product_id"), table_name="product_media")
    op.drop_table("product_media")
    op.execute("DROP TYPE IF EXISTS media_type_enum;")
