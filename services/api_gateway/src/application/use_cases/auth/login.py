from src.domain.dtos.auth import AuthTokens, LoginInput
from src.domain.interfaces.auth_gateway import AbstractAuthGateway


class LoginUseCase:
    def __init__(self, auth: AbstractAuthGateway) -> None:
        self._auth = auth

    async def execute(self, data: LoginInput) -> AuthTokens:
        return await self._auth.login(data)
