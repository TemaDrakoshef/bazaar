from src.domain.dtos.auth import AuthTokens, SignUpInput
from src.domain.interfaces.auth_gateway import AbstractAuthGateway


class SignUpUseCase:
    def __init__(self, auth: AbstractAuthGateway) -> None:
        self._auth = auth

    async def execute(self, data: SignUpInput) -> AuthTokens:
        return await self._auth.sign_up(data)
