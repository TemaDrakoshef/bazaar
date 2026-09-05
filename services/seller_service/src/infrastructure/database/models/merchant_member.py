from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class MerchantMemberORM(Base):
    """A user's membership in a merchant organization."""

    __tablename__ = "merchant_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    merchant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="VIEWER")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint(
            "merchant_id", "user_id", name="uq_merchant_members_merchant_user"
        ),
        Index("ix_merchant_members_merchant_id", "merchant_id"),
        Index("ix_merchant_members_user_id", "user_id"),
    )
