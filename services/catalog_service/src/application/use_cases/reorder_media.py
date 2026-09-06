import structlog

from src.domain.dtos.media import ReorderMediaRequest
from src.domain.exceptions import (
    AccessDeniedError,
    MediaValidationError,
    ProductNotFoundError,
)
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class ReorderMediaUseCase:
    """Batch-update media positions of one product."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, request: ReorderMediaRequest) -> None:
        media_ids = [item.media_id for item in request.items]
        if len(media_ids) != len(set(media_ids)):
            raise MediaValidationError("duplicate media ids in reorder request")

        async with self._uow as uow:
            product = await uow.product.get_by_id(request.product_id)
            if not product:
                raise ProductNotFoundError(str(request.product_id))
            if product.merchant_id != request.merchant_id:
                raise AccessDeniedError()

            records = await uow.media.list_by_ids(media_ids)
            if len(records) != len(media_ids):
                raise MediaValidationError("unknown media ids in reorder request")
            for record in records:
                if record.product_id != request.product_id:
                    raise MediaValidationError("media does not belong to the product")

            await uow.media.update_positions(
                [(item.media_id, item.position) for item in request.items]
            )
            await uow.commit()

        logger.info(
            "media.reordered",
            product_id=request.product_id,
            merchant_id=request.merchant_id,
            items=request.items,
        )
