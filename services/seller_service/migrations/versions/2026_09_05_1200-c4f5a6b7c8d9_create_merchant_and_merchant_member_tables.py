"""Create Merchant and MerchantMember tables

Revision ID: c4f5a6b7c8d9
Revises:
Create Date: 2026-09-05 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4f5a6b7c8d9"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the merchants and merchant_members tables."""
    op.create_table(
        "merchants",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("inn", sa.String(length=12), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchants_inn_unique", "merchants", ["inn"], unique=True)
    op.create_index(
        "ix_merchants_owner_user_id", "merchants", ["owner_user_id"], unique=False
    )
    op.create_check_constraint(
        "ck_merchants_status",
        "merchants",
        "status IN ('ACTIVE', 'PENDING_VERIFICATION')",
    )

    op.create_table(
        "merchant_members",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("merchant_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "merchant_id", "user_id", name="uq_merchant_members_merchant_user"
        ),
    )
    op.create_index(
        "ix_merchant_members_merchant_id",
        "merchant_members",
        ["merchant_id"],
        unique=False,
    )
    op.create_index(
        "ix_merchant_members_user_id",
        "merchant_members",
        ["user_id"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_merchant_members_role",
        "merchant_members",
        "role IN ('OWNER', 'MANAGER', 'VIEWER')",
    )


def downgrade() -> None:
    """Drop the merchant_members and merchants tables."""
    op.drop_index("ix_merchant_members_user_id", table_name="merchant_members")
    op.drop_index("ix_merchant_members_merchant_id", table_name="merchant_members")
    op.drop_constraint("ck_merchant_members_role", "merchant_members", type_="check")
    op.drop_table("merchant_members")

    op.drop_index("ix_merchants_owner_user_id", table_name="merchants")
    op.drop_index("ix_merchants_inn_unique", table_name="merchants")
    op.drop_constraint("ck_merchants_status", "merchants", type_="check")
    op.drop_table("merchants")
