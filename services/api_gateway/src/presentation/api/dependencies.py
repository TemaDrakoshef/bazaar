from dataclasses import dataclass
from typing import Annotated

from dishka import AsyncContainer
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.application.use_cases.seller.verify_access import VerifyAccessUseCase
from src.domain.dtos.auth import ValidateTokenInput
from src.domain.dtos.seller import VerifyAccessInput
from src.domain.exceptions import PermissionDeniedError

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class MerchantContext:
    """Merchant context resolved for the current request."""

    user_id: str
    merchant_id: int
    role: str


async def get_validate_token_use_case(request: Request) -> ValidateTokenUseCase:
    """Resolve the validate-token use case from the dishka request container."""
    container: AsyncContainer = request.state.dishka_container
    return await container.get(ValidateTokenUseCase)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    validate_token: ValidateTokenUseCase = Depends(get_validate_token_use_case),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response = await validate_token.execute(
        ValidateTokenInput(access_token=credentials.credentials)
    )
    if not response.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.error_message or "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response.user_id or ""


async def get_verify_access_use_case(request: Request) -> VerifyAccessUseCase:
    """Resolve the verify-access use case from the dishka request container."""
    container: AsyncContainer = request.state.dishka_container
    return await container.get(VerifyAccessUseCase)


async def get_current_merchant_context(
    request: Request,
    x_merchant_id: Annotated[int | None, Header(alias="X-Merchant-ID")] = None,
    user_id: str = Depends(get_current_user_id),
    verify_access: VerifyAccessUseCase = Depends(get_verify_access_use_case),
) -> MerchantContext:
    """Resolve the active merchant for the request.

    Requires the ``X-Merchant-ID`` header, verifies via seller_service that the
    authenticated user is an active member of that merchant, and returns the
    context (403 when the check fails).
    """
    if x_merchant_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="X-Merchant-ID header is required",
        )
    result = await verify_access.execute(
        VerifyAccessInput(user_id=user_id, merchant_id=x_merchant_id)
    )
    if not result.allowed:
        raise PermissionDeniedError("no access to the requested merchant")
    return MerchantContext(user_id=user_id, merchant_id=x_merchant_id, role=result.role)
