from datetime import datetime

from pydantic import BaseModel, Field


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


class ProductResult(BaseModel):
    id: int
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListQuery(BaseModel):
    limit: int = 20
    offset: int = 0


class ProductListResult(BaseModel):
    products: list[ProductResult]
    count: int
