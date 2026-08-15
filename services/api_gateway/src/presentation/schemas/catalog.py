from datetime import datetime

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: int
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreateRequest(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)


class ProductUpdateRequest(BaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    count: int


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryCreateRequest(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryUpdateRequest(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class CategoryMoveRequest(BaseModel):
    parent_id: int | None = None
