"""Create Product and Category tables"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d3a8bd4ec0f9"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree;")

    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sqlalchemy_utils.types.ltree.LtreeType(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_categories_path",
        "categories",
        ["path"],
        unique=False,
        postgresql_using="gist",
    )
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_products_category_id"), "products", ["category_id"], unique=False
    )
    op.create_check_constraint(
        "ck_products_price_non_negative", "products", "price >= 0"
    )
    op.create_check_constraint(
        "ck_products_stock_non_negative", "products", "stock >= 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_products_category_id"), table_name="products")
    op.drop_table("products")

    op.drop_index(
        "ix_categories_path", table_name="categories", postgresql_using="gist"
    )
    op.drop_table("categories")
    op.drop_check_constraint("ck_products_price_non_negative", "products")
    op.drop_check_constraint("ck_products_stock_non_negative", "products")

    op.execute("DROP EXTENSION IF EXISTS ltree;")
