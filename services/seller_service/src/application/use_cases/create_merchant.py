import structlog

from src.domain.dtos.merchant import MerchantCreateDTO
from src.domain.entities.merchant import Merchant
from src.domain.exceptions import MerchantAlreadyExistsError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class CreateMerchantUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, data: MerchantCreateDTO) -> Merchant:
        """Register a merchant and add the requester as its OWNER."""
        async with self._uow as uow:
            existing = await uow.merchant.get_one_or_none(inn=data.inn)
            if existing:
                raise MerchantAlreadyExistsError(data.inn)

            merchant = await uow.merchant.create(
                name=data.name,
                inn=data.inn,
                owner_user_id=data.user_id,
                status="ACTIVE",
            )
            await uow.member.create(
                merchant_id=merchant.id,
                user_id=data.user_id,
                role="OWNER",
                is_active=True,
            )
            await uow.commit()

            refreshed = await uow.merchant.get_by_id(merchant.id)
            response = Merchant.model_validate(refreshed)

        logger.info(
            "merchant.created",
            merchant_id=response.id,
            name=response.name,
            owner_user_id=response.owner_user_id,
        )
        return response
