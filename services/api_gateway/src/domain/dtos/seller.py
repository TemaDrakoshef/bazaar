from datetime import datetime

from pydantic import BaseModel, Field


class MerchantCreateInput(BaseModel):
    """Gateway-layer input for registering a new merchant (shop)."""

    name: str = Field(min_length=1, max_length=255)
    inn: str = Field(pattern=r"^\d{10}$|^\d{12}$")
    user_id: str = Field(min_length=1)


class MerchantResult(BaseModel):
    """A merchant as returned by seller_service."""

    id: int
    name: str
    inn: str
    owner_user_id: str
    status: str
    created_at: datetime


class VerifyAccessInput(BaseModel):
    user_id: str
    merchant_id: int


class VerifyAccessResult(BaseModel):
    allowed: bool
    role: str = ""
