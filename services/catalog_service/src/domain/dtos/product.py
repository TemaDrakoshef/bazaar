from src.domain.entities.base import CustomModel


class ProductCreateDTO(CustomModel):
    category_id: int
    title: str
    description: str | None = None
    price: int
    stock: int
