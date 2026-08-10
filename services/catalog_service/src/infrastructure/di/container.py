from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.use_cases.create_category import CreateCategoryUseCase
from src.application.use_cases.create_product import CreateProductUseCase
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CatalogProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    async def provide_engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(settings.DATABASE_URL)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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

    @provide(scope=Scope.REQUEST)
    def provide_create_category(self, uow: AbstractUnitOfWork) -> CreateCategoryUseCase:
        return CreateCategoryUseCase(uow)
