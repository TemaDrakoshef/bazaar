from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AccountBase(BaseModel):
    id: UUID
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
