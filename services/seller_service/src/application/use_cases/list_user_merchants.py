from src.domain.entities.merchant import Merchant
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ListUserMerchantsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, user_id: str) -> list[Merchant]:
        """Return every active merchant the user has an active membership in."""
        async with self._uow as uow:
            members = await uow.member.get_all_by_filter(
                user_id=user_id, is_active=True
            )
            merchants: list[Merchant] = []
            for member in members:
                merchant = await uow.merchant.get_by_id(member.merchant_id)
                if merchant and merchant.status == "ACTIVE":
                    merchants.append(Merchant.model_validate(merchant))
            return merchants
