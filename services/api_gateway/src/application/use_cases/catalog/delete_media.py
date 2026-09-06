from src.domain.dtos.catalog import DeleteMediaInput
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class DeleteMediaUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, data: DeleteMediaInput) -> None:
        await self._catalog.delete_media(data)
