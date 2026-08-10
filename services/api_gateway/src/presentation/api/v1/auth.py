from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from src.application.use_cases.auth.login import LoginUseCase
from src.application.use_cases.auth.logout import LogoutUseCase
from src.application.use_cases.auth.refresh import RefreshUseCase
from src.application.use_cases.auth.signup import SignUpUseCase
from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.domain.dtos.auth import (
    LoginInput,
    LogoutInput,
    RefreshInput,
    SignUpInput,
    ValidateTokenInput,
)
from src.presentation.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    SignUpRequest,
    SignUpResponse,
    ValidateRequest,
    ValidateResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignUpResponse, status_code=201)
@inject
async def sign_up(
    body: SignUpRequest,
    use_case: FromDishka[SignUpUseCase],
) -> SignUpResponse:
    result = await use_case.execute(SignUpInput(**body.model_dump()))
    return SignUpResponse(**result.model_dump())


@router.post("/login", response_model=LoginResponse)
@inject
async def login(
    body: LoginRequest,
    use_case: FromDishka[LoginUseCase],
) -> LoginResponse:
    result = await use_case.execute(LoginInput(**body.model_dump()))
    return LoginResponse(**result.model_dump())


@router.post("/logout", status_code=204)
@inject
async def logout(
    body: LogoutRequest,
    use_case: FromDishka[LogoutUseCase],
) -> None:
    await use_case.execute(LogoutInput(**body.model_dump()))


@router.post("/refresh", response_model=RefreshResponse)
@inject
async def refresh(
    body: RefreshRequest,
    use_case: FromDishka[RefreshUseCase],
) -> RefreshResponse:
    result = await use_case.execute(RefreshInput(**body.model_dump()))
    return RefreshResponse(**result.model_dump())


@router.post("/validate", response_model=ValidateResponse)
@inject
async def validate_token(
    body: ValidateRequest,
    use_case: FromDishka[ValidateTokenUseCase],
) -> ValidateResponse:
    result = await use_case.execute(ValidateTokenInput(**body.model_dump()))
    return ValidateResponse(**result.model_dump())
