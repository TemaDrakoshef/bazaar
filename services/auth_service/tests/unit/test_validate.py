"""Unit tests for the ValidateToken usecase (no database)."""

from jose import jwt

from src.core.settings import settings
from src.usecase.base import AuthBaseUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.usecase import ValidateTokenUsecase


def _access_token(user_id: str) -> str:
    return AuthBaseUsecase.create_access_token(user_id)


async def test_validate_valid_token():
    token = _access_token("123e4567-e89b-12d3-a456-426614174000")
    result = await ValidateTokenUsecase().execute(
        ValidateTokenRequest(access_token=token)
    )
    assert result.valid is True
    assert result.user_id == "123e4567-e89b-12d3-a456-426614174000"
    assert result.error_message == ""


async def test_validate_invalid_token():
    result = await ValidateTokenUsecase().execute(
        ValidateTokenRequest(access_token="garbage.token.value")
    )
    assert result.valid is False
    assert result.user_id is None
    assert result.error_message == "Invalid token"


async def test_validate_token_without_user_id():
    token = jwt.encode(
        {"exp": 9999999999}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    result = await ValidateTokenUsecase().execute(
        ValidateTokenRequest(access_token=token)
    )
    assert result.valid is False
    assert result.error_message == "Invalid token"
