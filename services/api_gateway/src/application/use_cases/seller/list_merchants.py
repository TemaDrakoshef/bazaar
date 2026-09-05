from src.domain.dtos.seller import MerchantResult
from src.domain.interfaces.seller_gateway import AbstractSellerGateway


class ListUserMerchantsUseCase:
    def __init__(self, seller: AbstractSellerGateway) -> None:
        self._seller = seller

    async def execute(self, user_id: str) -> list[MerchantResult]:
        return await self._seller.list_user_merchants(user_id)
