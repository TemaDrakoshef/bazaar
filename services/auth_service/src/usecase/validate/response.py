from pydantic import BaseModel


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: str | None = None
    error_message: str = ""
