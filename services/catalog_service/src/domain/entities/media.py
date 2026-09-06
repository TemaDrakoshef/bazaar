from enum import StrEnum

from src.domain.entities.base import CustomModel


class MediaType(StrEnum):
    """Types of product media."""

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class ProductMedia(CustomModel):
    """Media record attached to a product."""

    id: int
    product_id: int
    media_type: MediaType
    url: str
    position: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None
    file_size: int
