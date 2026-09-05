from datetime import datetime

from pydantic import BaseModel, Field


class MerchantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    inn: str = Field(pattern=r"^\d{10}$|^\d{12}$")


class MerchantResponse(BaseModel):
    id: int
    name: str
    inn: str
    owner_user_id: str
    status: str
    created_at: datetime
