from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.merchant_member import MerchantMemberORM
from src.infrastructure.database.repositories.base import BaseRepository


class MerchantMemberRepository(BaseRepository):
    """Repository for managing MerchantMember entities in the database."""

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=MerchantMemberORM)
