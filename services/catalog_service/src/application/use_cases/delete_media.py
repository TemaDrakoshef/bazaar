import structlog

from src.domain.dtos.media import DeleteMediaRequest
from src.domain.exceptions import (
    AccessDeniedError,
    MediaNotFoundError,
    ProductNotFoundError,
)
from src.domain.interfaces.storage import AbstractStorageService
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class DeleteMediaUseCase:
    """Delete a media record from the database and its object from storage."""

    def __init__(
        self, uow: AbstractUnitOfWork, storage: AbstractStorageService
    ) -> None:
        self._uow = uow
        self._storage = storage

    async def __call__(self, request: DeleteMediaRequest) -> None:
        async with self._uow as uow:
            record = await uow.media.get_by_id(request.media_id)
            if not record or record.product_id != request.product_id:
                raise MediaNotFoundError(str(request.media_id))

            product = await uow.product.get_by_id(request.product_id)
            if not product:
                raise ProductNotFoundError(str(request.product_id))
            if product.merchant_id != request.merchant_id:
                raise AccessDeniedError()

            await self._storage.delete_object(record.storage_key)
            await uow.media.delete(request.media_id)
            await uow.commit()

        logger.info(
            "media.deleted",
            media_id=request.media_id,
            product_id=request.product_id,
            merchant_id=request.merchant_id,
        )
