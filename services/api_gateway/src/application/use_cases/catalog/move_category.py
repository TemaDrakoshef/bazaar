from src.domain.dtos.catalog import CategoryMoveDTO, CategoryResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class MoveCategoryUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, category_id: int, data: CategoryMoveDTO) -> CategoryResult:
        return await self._catalog.move_category(category_id, data)
