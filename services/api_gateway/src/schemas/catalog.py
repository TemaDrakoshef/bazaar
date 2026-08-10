from datetime import datetime

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreateRequest(BaseModel):
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int


class CategoryResponse(BaseModel):
    id: int
    name: str
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryCreateRequest(BaseModel):
    name: str
    parent_id: int | None = None
