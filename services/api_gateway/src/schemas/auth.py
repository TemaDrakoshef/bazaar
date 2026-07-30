from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: str
    phone: str
    password: str


class SignUpResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class LogoutRequest(BaseModel):
    session_id: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
