from src.domain.dtos.auth import TokenStatus, ValidateTokenInput
from src.domain.interfaces.auth_gateway import AbstractAuthGateway


class ValidateTokenUseCase:
    def __init__(self, auth: AbstractAuthGateway) -> None:
        self._auth = auth

    async def execute(self, data: ValidateTokenInput) -> TokenStatus:
        return await self._auth.validate_token(data)
