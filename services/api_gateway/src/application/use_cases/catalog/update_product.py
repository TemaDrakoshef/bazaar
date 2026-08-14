from src.domain.dtos.catalog import ProductResult, ProductUpdateDTO
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class UpdateProductUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, product_id: int, data: ProductUpdateDTO) -> ProductResult:
        return await self._catalog.update_product(product_id, data)
