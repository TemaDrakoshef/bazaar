from src.domain.entities.base import CustomModel
from src.domain.entities.media import MediaType


class MediaUploadUrlRequest(CustomModel):
    product_id: int
    merchant_id: int
    media_type: MediaType
    content_type: str
    file_size: int


class MediaUploadUrlResult(CustomModel):
    upload_url: str
    storage_key: str
    public_url: str


class ConfirmMediaUploadRequest(CustomModel):
    product_id: int
    merchant_id: int
    media_type: MediaType
    storage_key: str
    public_url: str
    file_size: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None


class DeleteMediaRequest(CustomModel):
    product_id: int
    merchant_id: int
    media_id: int


class ReorderMediaItemDTO(CustomModel):
    media_id: int
    position: int


class ReorderMediaRequest(CustomModel):
    product_id: int
    merchant_id: int
    items: list[ReorderMediaItemDTO]
