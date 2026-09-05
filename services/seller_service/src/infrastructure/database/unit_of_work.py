from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.database.repositories.merchant import MerchantRepository
from src.infrastructure.database.repositories.merchant_member import (
    MerchantMemberRepository,
)


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.merchant = MerchantRepository(self._session)
        self.member = MerchantMemberRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
