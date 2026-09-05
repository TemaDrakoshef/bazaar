from src.domain.dtos.merchant import VerifyAccessDTO, VerifyAccessResult
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class VerifyAccessUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, data: VerifyAccessDTO) -> VerifyAccessResult:
        """Check whether ``user_id`` has an active membership in ``merchant_id``.

        Both the membership and the merchant itself must be active for access
        to be granted.
        """
        async with self._uow as uow:
            member = await uow.member.get_one_or_none(
                user_id=data.user_id, merchant_id=data.merchant_id
            )
            if not member or not member.is_active:
                return VerifyAccessResult(allowed=False)

            merchant = await uow.merchant.get_by_id(member.merchant_id)
            if not merchant or merchant.status != "ACTIVE":
                return VerifyAccessResult(allowed=False)

            return VerifyAccessResult(allowed=True, role=member.role)
