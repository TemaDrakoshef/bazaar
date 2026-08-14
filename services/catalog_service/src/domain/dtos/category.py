from src.domain.entities.base import CustomModel


class CategoryCreateDTO(CustomModel):
    name: str
    parent_id: int | None = None


class CategoryUpdateDTO(CustomModel):
    name: str | None = None
    path: str | None = None
    is_active: bool | None = None


class CategoryIdRequestDTO(CustomModel):
    category_id: int
