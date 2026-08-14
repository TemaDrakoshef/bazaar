from src.domain.dtos.catalog import CategoryResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class ReadCategoryUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, category_id: int) -> CategoryResult:
        return await self._catalog.read_category(category_id)
