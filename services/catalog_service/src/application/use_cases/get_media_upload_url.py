import uuid

import structlog

from src.application.media_rules import (
    validate_content_type,
    validate_file_size,
    validate_media_type,
)
from src.domain.dtos.media import MediaUploadUrlRequest, MediaUploadUrlResult
from src.domain.entities.media import MediaType
from src.domain.exceptions import (
    AccessDeniedError,
    ProductNotFoundError,
    VideoAlreadyExistsError,
)
from src.domain.interfaces.storage import AbstractStorageService
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class GetMediaUploadUrlUseCase:
    """Validate the upload request and return a presigned PUT URL for the file."""

    def __init__(
        self, uow: AbstractUnitOfWork, storage: AbstractStorageService
    ) -> None:
        self._uow = uow
        self._storage = storage

    async def __call__(self, request: MediaUploadUrlRequest) -> MediaUploadUrlResult:
        validate_media_type(request.media_type)
        extension = validate_content_type(request.media_type, request.content_type)
        validate_file_size(request.media_type, request.file_size)

        async with self._uow as uow:
            product = await uow.product.get_by_id(request.product_id)
            if not product:
                raise ProductNotFoundError(str(request.product_id))
            if product.merchant_id != request.merchant_id:
                raise AccessDeniedError()

            if request.media_type == MediaType.VIDEO:
                if await uow.media.has_video(request.product_id):
                    raise VideoAlreadyExistsError()

            folder = "videos" if request.media_type == MediaType.VIDEO else "images"
            key = f"products/{request.product_id}/{folder}/{uuid.uuid4()}.{extension}"
            upload_url = await self._storage.generate_presigned_upload_url(
                key=key,
                content_type=request.content_type,
                expires_in=600,
            )

        public_url = self._storage.public_url(key)
        logger.info(
            "media.upload_url_generated",
            product_id=request.product_id,
            merchant_id=request.merchant_id,
            media_type=request.media_type,
            storage_key=key,
        )
        return MediaUploadUrlResult(
            upload_url=upload_url,
            storage_key=key,
            public_url=public_url,
        )
