import grpc.aio
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.clients.auth_client import AuthClient
from src.dependencies import get_auth_client
from src.exceptions import grpc_error_to_http

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- Request / Response models ----------


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


# ---------- Endpoints ----------


@router.post("/signup", response_model=SignUpResponse, status_code=201)
async def sign_up(
    body: SignUpRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> SignUpResponse:
    try:
        resp = await auth_client.sign_up(
            email=body.email, phone=body.phone, password=body.password
        )
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc
    return SignUpResponse(
        access_token=resp.access_token, refresh_token=resp.refresh_token
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> LoginResponse:
    try:
        resp = await auth_client.login(email=body.email, password=body.password)
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc
    return LoginResponse(
        access_token=resp.access_token, refresh_token=resp.refresh_token
    )


@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> None:
    try:
        await auth_client.logout(session_id=body.session_id)
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    body: RefreshRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> RefreshResponse:
    try:
        resp = await auth_client.refresh(refresh_token=body.refresh_token)
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc
    return RefreshResponse(access_token=resp.access_token)
