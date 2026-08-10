from src.domain.dtos.auth import LogoutInput
from src.domain.interfaces.auth_gateway import AbstractAuthGateway


class LogoutUseCase:
    def __init__(self, auth: AbstractAuthGateway) -> None:
        self._auth = auth

    async def execute(self, data: LogoutInput) -> None:
        await self._auth.logout(data)
