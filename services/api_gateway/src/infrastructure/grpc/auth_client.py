import grpc.aio

from src.domain.dtos.auth import (
    AuthTokens,
    LoginInput,
    LogoutInput,
    RefreshInput,
    SignUpInput,
    TokenStatus,
    ValidateTokenInput,
)
from src.domain.interfaces.auth_gateway import AbstractAuthGateway
from src.generated.auth.v1 import auth_pb2, auth_pb2_grpc
from src.infrastructure.grpc.errors import translate_grpc_error
from src.infrastructure.grpc.logging import track_grpc_call


class AuthClient(AbstractAuthGateway):
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = auth_pb2_grpc.AuthServiceStub(channel)

    async def sign_up(self, data: SignUpInput) -> AuthTokens:
        async with track_grpc_call("auth", "SignUp"):
            try:
                response = await self._stub.SignUp(
                    auth_pb2.SignUpRequest(
                        email=data.email, phone=data.phone or "", password=data.password
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return AuthTokens(
            access_token=response.access_token, refresh_token=response.refresh_token
        )

    async def login(self, data: LoginInput) -> AuthTokens:
        async with track_grpc_call("auth", "Login"):
            try:
                response = await self._stub.Login(
                    auth_pb2.LoginRequest(email=data.email, password=data.password)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return AuthTokens(
            access_token=response.access_token, refresh_token=response.refresh_token
        )

    async def logout(self, data: LogoutInput) -> None:
        async with track_grpc_call("auth", "Logout"):
            try:
                await self._stub.Logout(
                    auth_pb2.LogoutRequest(session_id=data.session_id)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc

    async def refresh(self, data: RefreshInput) -> AuthTokens:
        async with track_grpc_call("auth", "Refresh"):
            try:
                response = await self._stub.Refresh(
                    auth_pb2.RefreshRequest(refresh_token=data.refresh_token)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return AuthTokens(
            access_token=response.access_token, refresh_token=response.refresh_token
        )

    async def validate_token(self, data: ValidateTokenInput) -> TokenStatus:
        async with track_grpc_call("auth", "ValidateToken"):
            try:
                response = await self._stub.ValidateToken(
                    auth_pb2.ValidateTokenRequest(access_token=data.access_token)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return TokenStatus(
            valid=response.valid,
            user_id=response.user_id if response.HasField("user_id") else None,
            error_message=response.error_message,
        )
