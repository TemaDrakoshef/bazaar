from src.domain.entities.base import CustomModel


class ProductCreateDTO(CustomModel):
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int


class ProductUpdateDTO(CustomModel):
    category_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    stock: int | None = None
    is_active: bool | None = None


class ProductListQueryDTO(CustomModel):
    limit: int = 20
    offset: int = 0
