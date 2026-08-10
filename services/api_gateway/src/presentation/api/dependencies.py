from dishka import AsyncContainer
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.domain.dtos.auth import ValidateTokenInput

_bearer = HTTPBearer(auto_error=False)


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
