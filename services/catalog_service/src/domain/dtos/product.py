from pydantic import Field

from src.domain.entities.base import CustomModel


class ProductCreateDTO(CustomModel):
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)


class ProductUpdateDTO(CustomModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductListQueryDTO(CustomModel):
    limit: int = 20
    offset: int = 0
