from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.merchant import MerchantORM
from src.infrastructure.database.repositories.base import BaseRepository


class MerchantRepository(BaseRepository):
    """Repository for managing Merchant entities in the database."""

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=MerchantORM)
