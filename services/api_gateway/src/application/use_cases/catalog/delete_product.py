from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class DeleteProductUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, product_id: int) -> None:
        await self._catalog.delete_product(product_id)
