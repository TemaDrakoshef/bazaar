from src.domain.dtos.catalog import CategoryCreateDTO, CategoryResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class CreateCategoryUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, data: CategoryCreateDTO) -> CategoryResult:
        return await self._catalog.create_category(data)
