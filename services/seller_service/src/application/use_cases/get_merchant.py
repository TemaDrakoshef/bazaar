from src.domain.entities.merchant import Merchant
from src.domain.exceptions import MerchantNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class GetMerchantUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, merchant_id: int) -> Merchant:
        async with self._uow as uow:
            merchant = await uow.merchant.get_by_id(merchant_id)
            if not merchant:
                raise MerchantNotFoundError(str(merchant_id))
            return Merchant.model_validate(merchant)
