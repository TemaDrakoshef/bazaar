from src.domain.dtos.auth import AccessToken, RefreshInput
from src.domain.interfaces.auth_gateway import AbstractAuthGateway


class RefreshUseCase:
    def __init__(self, auth: AbstractAuthGateway) -> None:
        self._auth = auth

    async def execute(self, data: RefreshInput) -> AccessToken:
        return await self._auth.refresh(data)
