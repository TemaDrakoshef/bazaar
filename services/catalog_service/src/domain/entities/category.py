from datetime import datetime

from src.domain.entities.base import CustomModel


class Category(CustomModel):
    id: int
    name: str
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
