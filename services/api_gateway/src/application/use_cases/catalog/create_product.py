from src.domain.dtos.catalog import ProductCreateDTO, ProductResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class CreateProductUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, data: ProductCreateDTO) -> ProductResult:
        return await self._catalog.create_product(data)
