from datetime import datetime

from pydantic import BaseModel


class CategoryCreateDTO(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryResult(BaseModel):
    id: int
    name: str
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
