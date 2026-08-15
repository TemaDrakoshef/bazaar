from pydantic import BaseModel


class SignUpInput(BaseModel):
    email: str
    phone: str | None = None
    password: str


class LoginInput(BaseModel):
    email: str
    password: str


class LogoutInput(BaseModel):
    session_id: str


class RefreshInput(BaseModel):
    refresh_token: str


class ValidateTokenInput(BaseModel):
    access_token: str


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str


class TokenStatus(BaseModel):
    valid: bool
    user_id: str | None = None
    error_message: str = ""
