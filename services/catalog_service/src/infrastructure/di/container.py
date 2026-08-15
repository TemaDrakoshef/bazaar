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
from src.application.use_cases.delete_category import DeleteCategoryUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.move_category import MoveCategoryUseCase
from src.application.use_cases.read_category import (
    ReadCategoryUseCase,
)
from src.application.use_cases.read_list_category import (
    ReadListCategoriesUseCase,
)
from src.application.use_cases.read_list_products import ReadListProductsUseCase
from src.application.use_cases.read_product import ReadProductUseCase
from src.application.use_cases.update_category import UpdateCategoryUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
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

    @provide(scope=Scope.REQUEST)
    def provide_read_category(self, uow: AbstractUnitOfWork) -> ReadCategoryUseCase:
        return ReadCategoryUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_read_list_categories(
        self, uow: AbstractUnitOfWork
    ) -> ReadListCategoriesUseCase:
        return ReadListCategoriesUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_read_product(self, uow: AbstractUnitOfWork) -> ReadProductUseCase:
        return ReadProductUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_read_list_products(
        self, uow: AbstractUnitOfWork
    ) -> ReadListProductsUseCase:
        return ReadListProductsUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_update_product(self, uow: AbstractUnitOfWork) -> UpdateProductUseCase:
        return UpdateProductUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_delete_product(self, uow: AbstractUnitOfWork) -> DeleteProductUseCase:
        return DeleteProductUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_update_category(self, uow: AbstractUnitOfWork) -> UpdateCategoryUseCase:
        return UpdateCategoryUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_delete_category(self, uow: AbstractUnitOfWork) -> DeleteCategoryUseCase:
        return DeleteCategoryUseCase(uow)

    @provide(scope=Scope.REQUEST)
    def provide_move_category(self, uow: AbstractUnitOfWork) -> MoveCategoryUseCase:
        return MoveCategoryUseCase(uow)
