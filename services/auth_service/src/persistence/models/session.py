import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.persistence.models.base import Base


class Session(Base):
    """Represents a user session in the system."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    refresh_token_hash: Mapped[str | None] = mapped_column(nullable=True)
    last_active_at: Mapped[datetime.datetime] = mapped_column(nullable=False)
