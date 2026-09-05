from src.domain.dtos.seller import VerifyAccessInput, VerifyAccessResult
from src.domain.interfaces.seller_gateway import AbstractSellerGateway


class VerifyAccessUseCase:
    def __init__(self, seller: AbstractSellerGateway) -> None:
        self._seller = seller

    async def execute(self, data: VerifyAccessInput) -> VerifyAccessResult:
        return await self._seller.verify_access(data)
