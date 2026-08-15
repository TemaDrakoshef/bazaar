from datetime import datetime

from pydantic import Field

from src.domain.entities.base import CustomModel


class Product(CustomModel):
    id: int
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreate(CustomModel):
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
