from src.domain.dtos.catalog import (
    MediaUploadUrlInput,
    MediaUploadUrlResult,
)
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway


class GetMediaUploadUrlUseCase:
    def __init__(self, catalog: AbstractCatalogGateway) -> None:
        self._catalog = catalog

    async def execute(self, data: MediaUploadUrlInput) -> MediaUploadUrlResult:
        return await self._catalog.get_media_upload_url(data)
