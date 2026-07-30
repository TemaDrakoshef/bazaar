from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.account import Account
from src.persistence.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    """Repository for managing Account entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the AccountRepository with a database session."""

        super().__init__(session=session, model=Account)
