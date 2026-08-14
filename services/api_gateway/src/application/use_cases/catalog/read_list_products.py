from src.domain.dtos.catalog import ProductListQuery, ProductListResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class ReadListProductsUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, query: ProductListQuery) -> ProductListResult:
        return await self._catalog.read_list_products(query)
