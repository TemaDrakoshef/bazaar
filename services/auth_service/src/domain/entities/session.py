import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionBase(BaseModel):
    id: UUID
    user_id: UUID
    token: UUID
    is_active: bool
    refresh_token_hash: str | None = None
    last_active_at: datetime.datetime
