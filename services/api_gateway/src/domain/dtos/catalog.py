from pydantic import BaseModel


class CategoryCreateDTO(BaseModel):
    name: str
    parent_id: int | None = None
