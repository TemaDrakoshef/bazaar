from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import LtreeType

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.product import (
        ProductORM,
    )


class CategoryORM(Base):
    """Represents a product category using PostgreSQL LTREE.

    ``parent_id`` is the source of structural integrity, while ``path`` is a
    denormalized LTREE used for fast ancestor/subtree queries.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    path: Mapped[str] = mapped_column(LtreeType, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now, onupdate=datetime.now
    )

    products: Mapped[list["ProductORM"]] = relationship(
        "ProductORM", back_populates="category"
    )

    parent: Mapped["CategoryORM | None"] = relationship(
        "CategoryORM", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["CategoryORM"]] = relationship(
        "CategoryORM", back_populates="parent"
    )

    __table_args__ = (Index("ix_categories_path", "path", postgresql_using="gist"),)
