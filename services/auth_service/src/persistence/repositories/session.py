from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.session import Session
from src.persistence.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    """Repository for managing Session entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the SessionRepository with a database session."""

        super().__init__(session=session, model=Session)
