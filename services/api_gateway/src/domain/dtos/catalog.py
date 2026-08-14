from datetime import datetime

from pydantic import BaseModel


class CategoryCreateDTO(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryUpdateDTO(BaseModel):
    name: str | None = None
    path: str | None = None
    is_active: bool | None = None


class CategoryResult(BaseModel):
    id: int
    name: str
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryListQuery(BaseModel):
    limit: int = 20
    offset: int = 0


class ProductCreateDTO(BaseModel):
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int


class ProductUpdateDTO(BaseModel):
    category_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    stock: int | None = None
    is_active: bool | None = None


class ProductResult(BaseModel):
    id: int
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListQuery(BaseModel):
    limit: int = 20
    offset: int = 0


class ProductListResult(BaseModel):
    products: list[ProductResult]
    count: int
