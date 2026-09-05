from src.domain.dtos.seller import MerchantCreateInput, MerchantResult
from src.domain.interfaces.seller_gateway import AbstractSellerGateway


class CreateMerchantUseCase:
    def __init__(self, seller: AbstractSellerGateway) -> None:
        self._seller = seller

    async def execute(self, data: MerchantCreateInput) -> MerchantResult:
        return await self._seller.create_merchant(data)
