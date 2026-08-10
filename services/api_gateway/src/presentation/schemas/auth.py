from pydantic import BaseModel, EmailStr, Field

_PHONE_PATTERN = r"^\+[1-9][0-9]{6,14}$"

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 100


class SignUpRequest(BaseModel):
    email: EmailStr
    phone: str | None = Field(default=None, pattern=_PHONE_PATTERN)
    password: str = Field(
        min_length=_PASSWORD_MIN_LENGTH, max_length=_PASSWORD_MAX_LENGTH
    )


class SignUpResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=_PASSWORD_MIN_LENGTH, max_length=_PASSWORD_MAX_LENGTH
    )


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class LogoutRequest(BaseModel):
    session_id: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class RefreshResponse(BaseModel):
    access_token: str


class ValidateRequest(BaseModel):
    access_token: str = Field(min_length=1)


class ValidateResponse(BaseModel):
    valid: bool
    user_id: str | None = None
    error_message: str = ""
