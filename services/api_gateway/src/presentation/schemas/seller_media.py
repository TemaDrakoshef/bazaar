from pydantic import BaseModel, Field

from src.domain.dtos.catalog import MediaType


class GetUploadUrlSchemaIn(BaseModel):
    media_type: MediaType
    content_type: str = Field(min_length=1, max_length=128)
    file_size: int = Field(gt=0)


class GetUploadUrlSchemaOut(BaseModel):
    upload_url: str
    storage_key: str
    public_url: str


class ConfirmUploadSchemaIn(BaseModel):
    media_type: MediaType
    storage_key: str = Field(min_length=1, max_length=512)
    public_url: str = Field(min_length=1, max_length=1024)
    file_size: int = Field(gt=0)
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)
    duration_seconds: int | None = Field(default=None, ge=0)


class MediaPositionItem(BaseModel):
    media_id: int
    position: int = Field(ge=0)


class ReorderMediaSchemaIn(BaseModel):
    items: list[MediaPositionItem] = Field(min_length=1)


class MediaResponse(BaseModel):
    id: int
    product_id: int
    media_type: MediaType
    url: str
    position: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None
    file_size: int
