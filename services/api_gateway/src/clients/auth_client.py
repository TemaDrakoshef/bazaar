import grpc.aio

from src.generated.auth.v1 import auth_pb2, auth_pb2_grpc


class AuthClient:
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = auth_pb2_grpc.AuthServiceStub(channel)

    async def sign_up(
        self, email: str, phone: str, password: str
    ) -> auth_pb2.SignUpResponse:
        return await self._stub.SignUp(
            auth_pb2.SignUpRequest(email=email, phone=phone, password=password)
        )

    async def login(self, email: str, password: str) -> auth_pb2.LoginResponse:
        return await self._stub.Login(
            auth_pb2.LoginRequest(email=email, password=password)
        )

    async def logout(self, session_id: str) -> auth_pb2.LogoutResponse:
        return await self._stub.Logout(auth_pb2.LogoutRequest(session_id=session_id))

    async def refresh(self, refresh_token: str) -> auth_pb2.RefreshResponse:
        return await self._stub.Refresh(
            auth_pb2.RefreshRequest(refresh_token=refresh_token)
        )

    async def validate_token(self, access_token: str) -> auth_pb2.ValidateTokenResponse:
        return await self._stub.ValidateToken(
            auth_pb2.ValidateTokenRequest(access_token=access_token)
        )
