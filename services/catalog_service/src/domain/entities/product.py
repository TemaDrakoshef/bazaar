from datetime import datetime

from src.domain.entities.base import CustomModel


class Product(CustomModel):
    id: int
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreate(CustomModel):
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int
