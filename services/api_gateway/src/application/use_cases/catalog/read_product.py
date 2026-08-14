from src.domain.dtos.catalog import ProductResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class ReadProductUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, product_id: int) -> ProductResult:
        return await self._catalog.read_product(product_id)
