from src.domain.entities.base import CustomModel


class CategoryCreateDTO(CustomModel):
    name: str
    parent_id: int | None = None
