from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MediaType(StrEnum):
    """Media types accepted by the catalog media API."""

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class CategoryCreateDTO(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryUpdateDTO(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class CategoryMoveDTO(BaseModel):
    parent_id: int | None = None


class CategoryResult(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryListQuery(BaseModel):
    limit: int = 20
    offset: int = 0


class ProductCreateDTO(BaseModel):
    merchant_id: int
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)


class ProductUpdateDTO(BaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductMediaResult(BaseModel):
    id: int
    product_id: int
    media_type: MediaType
    url: str
    position: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None
    file_size: int


class ProductResult(BaseModel):
    id: int
    merchant_id: int
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    media: list[ProductMediaResult] = Field(default_factory=list)


class ProductListQuery(BaseModel):
    limit: int = 20
    offset: int = 0
    merchant_id: int | None = None


class ProductListResult(BaseModel):
    products: list[ProductResult]
    count: int


class MediaUploadUrlInput(BaseModel):
    product_id: int
    merchant_id: int
    media_type: MediaType
    content_type: str
    file_size: int


class MediaUploadUrlResult(BaseModel):
    upload_url: str
    storage_key: str
    public_url: str


class ConfirmMediaUploadInput(BaseModel):
    product_id: int
    merchant_id: int
    media_type: MediaType
    storage_key: str
    public_url: str
    file_size: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None


class DeleteMediaInput(BaseModel):
    product_id: int
    merchant_id: int
    media_id: int


class ReorderMediaItemInput(BaseModel):
    media_id: int
    position: int


class ReorderMediaInput(BaseModel):
    product_id: int
    merchant_id: int
    items: list[ReorderMediaItemInput]
