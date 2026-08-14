from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class DeleteCategoryUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, category_id: int) -> None:
        await self._catalog.delete_category(category_id)
