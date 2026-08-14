from src.domain.dtos.catalog import CategoryListQuery, CategoryResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class ReadListCategoriesUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, query: CategoryListQuery) -> list[CategoryResult]:
        return await self._catalog.read_list_categories(query)
