from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.use_cases.create_merchant import CreateMerchantUseCase
from src.application.use_cases.get_merchant import GetMerchantUseCase
from src.application.use_cases.list_user_merchants import ListUserMerchantsUseCase
from src.application.use_cases.verify_access import VerifyAccessUseCase
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class SellerProvider(Provider):
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
    def provide_create_merchant(self, uow: AbstractUnitOfWork) -> CreateMerchantUseCase:
        return CreateMerchantUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_get_merchant(self, uow: AbstractUnitOfWork) -> GetMerchantUseCase:
        return GetMerchantUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_list_user_merchants(
        self, uow: AbstractUnitOfWork
    ) -> ListUserMerchantsUseCase:
        return ListUserMerchantsUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_verify_access(self, uow: AbstractUnitOfWork) -> VerifyAccessUseCase:
        return VerifyAccessUseCase(uow)
