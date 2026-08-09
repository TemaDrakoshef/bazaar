from collections.abc import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.infrastructure.database.repositories.category import CategoryRepository
from src.infrastructure.database.repositories.product import ProductRepository


class SQLAlchemyUnitOfWork:
    def __init__(self, session_maker: async_sessionmaker):
        self._session_maker = session_maker

    async def __aenter__(self):
        self._session = self._session_maker()
        self.product = ProductRepository(self._session)
        self.category = CategoryRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()


UowFactory = Callable[[], SQLAlchemyUnitOfWork]
