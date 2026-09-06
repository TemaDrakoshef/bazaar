import structlog

from src.application.media_rules import validate_file_size, validate_media_type
from src.domain.dtos.media import ConfirmMediaUploadRequest
from src.domain.entities.media import MediaType, ProductMedia
from src.domain.exceptions import (
    AccessDeniedError,
    MediaValidationError,
    ProductNotFoundError,
    VideoAlreadyExistsError,
)
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()

_KEY_PREFIX_TEMPLATE = "products/{product_id}/"


class ConfirmMediaUploadUseCase:
    """Register an already-uploaded object as product media."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, request: ConfirmMediaUploadRequest) -> ProductMedia:
        validate_media_type(request.media_type)
        validate_file_size(request.media_type, request.file_size)

        expected_prefix = _KEY_PREFIX_TEMPLATE.format(product_id=request.product_id)
        if not request.storage_key.startswith(expected_prefix):
            raise MediaValidationError("storage_key does not belong to the product")

        async with self._uow as uow:
            product = await uow.product.get_by_id(request.product_id)
            if not product:
                raise ProductNotFoundError(str(request.product_id))
            if product.merchant_id != request.merchant_id:
                raise AccessDeniedError()

            if request.media_type == MediaType.VIDEO:
                if await uow.media.has_video(request.product_id):
                    raise VideoAlreadyExistsError()

            position = await uow.media.next_position(request.product_id)
            record = await uow.media.create(
                product_id=request.product_id,
                media_type=request.media_type.value,
                storage_key=request.storage_key,
                url=request.public_url,
                position=position,
                width=request.width,
                height=request.height,
                duration_seconds=request.duration_seconds,
                file_size=request.file_size,
            )
            await uow.commit()

            refreshed = await uow.media.get_by_id(record.id)
            response = ProductMedia.model_validate(refreshed)

        logger.info(
            "media.confirmed",
            media_id=response.id,
            product_id=request.product_id,
            media_type=request.media_type,
            position=response.position,
        )
        return response
