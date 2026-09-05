from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class DeleteProductUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, merchant_id: int, product_id: int) -> None:
        await self._catalog.delete_product(merchant_id, product_id)
