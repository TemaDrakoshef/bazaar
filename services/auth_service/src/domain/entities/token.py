from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    jwt_string: str
    user_id: UUID | None = None
    session_id: UUID | None = None
    exp: float
