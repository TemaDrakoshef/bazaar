from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.use_cases.create_product import CreateProductUseCase
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.database.database import async_session_maker
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CatalogProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return async_session_maker

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST, provides=AbstractUnitOfWork)
    def provide_uow(self, session: AsyncSession) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    def provide_create_product(self, uow: AbstractUnitOfWork) -> CreateProductUseCase:
        return CreateProductUseCase(uow)
