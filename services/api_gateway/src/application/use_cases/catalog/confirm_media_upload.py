from src.domain.dtos.catalog import (
    ConfirmMediaUploadInput,
    ProductMediaResult,
)
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class ConfirmMediaUploadUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, data: ConfirmMediaUploadInput) -> ProductMediaResult:
        return await self._catalog.confirm_media_upload(data)
