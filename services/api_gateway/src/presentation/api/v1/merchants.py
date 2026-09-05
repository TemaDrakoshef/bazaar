from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from src.application.use_cases.seller.create_merchant import CreateMerchantUseCase
from src.application.use_cases.seller.list_merchants import ListUserMerchantsUseCase
from src.domain.dtos.seller import MerchantCreateInput
from src.presentation.api.dependencies import get_current_user_id
from src.presentation.schemas.seller import MerchantCreateRequest, MerchantResponse

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.post("", response_model=MerchantResponse, status_code=201)
@inject
async def create_merchant(
    data: MerchantCreateRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: FromDishka[CreateMerchantUseCase],
) -> MerchantResponse:
    """Register a new merchant (shop); the caller becomes its OWNER."""
    result = await use_case.execute(
        MerchantCreateInput(name=data.name, inn=data.inn, user_id=user_id)
    )
    return MerchantResponse(**result.model_dump())


@router.get("/my", response_model=list[MerchantResponse])
@inject
async def list_my_merchants(
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: FromDishka[ListUserMerchantsUseCase],
) -> list[MerchantResponse]:
    """List merchants the current user is a member of."""
    result = await use_case.execute(user_id)
    return [MerchantResponse(**merchant.model_dump()) for merchant in result]
