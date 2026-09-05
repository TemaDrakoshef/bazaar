from datetime import datetime

from sqlalchemy import BigInteger, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class MerchantORM(Base):
    """Aggregate root: a seller organization (ИП/ООО shop)."""

    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)

    __table_args__ = (
        Index("ix_merchants_inn_unique", "inn", unique=True),
        Index("ix_merchants_owner_user_id", "owner_user_id"),
    )
