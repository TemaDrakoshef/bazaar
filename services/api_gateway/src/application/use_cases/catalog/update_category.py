from src.domain.dtos.catalog import CategoryResult, CategoryUpdateDTO
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class UpdateCategoryUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(
        self, category_id: int, data: CategoryUpdateDTO
    ) -> CategoryResult:
        return await self._catalog.update_category(category_id, data)
