from datetime import datetime

from src.domain.entities.base import CustomModel


class Merchant(CustomModel):
    id: int
    name: str
    inn: str
    owner_user_id: str
    status: str  # ACTIVE | PENDING_VERIFICATION
    created_at: datetime


class MerchantMember(CustomModel):
    id: int
    merchant_id: int
    user_id: str
    role: str  # OWNER | MANAGER | VIEWER
    is_active: bool
