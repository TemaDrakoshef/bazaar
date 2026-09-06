from datetime import datetime

from pydantic import Field

from src.domain.entities.base import CustomModel
from src.domain.entities.media import ProductMedia


class Product(CustomModel):
    id: int
    merchant_id: int = Field(gt=0)
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    media: list[ProductMedia] = Field(default_factory=list)


class ProductCreate(CustomModel):
    merchant_id: int = Field(gt=0)
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
