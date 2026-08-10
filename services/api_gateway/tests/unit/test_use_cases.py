"""Unit tests for the application layer (use cases).

Each use case is exercised against a mocked gateway port, verifying the DTO is
forwarded untouched and gateway errors propagate unchanged.
"""

from __future__ import annotations

import pytest

from src.application.use_cases.auth.login import LoginUseCase
from src.application.use_cases.auth.logout import LogoutUseCase
from src.application.use_cases.auth.refresh import RefreshUseCase
from src.application.use_cases.auth.signup import SignUpUseCase
from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.application.use_cases.catalog.create_category import CreateCategoryUseCase
from src.domain.dtos.auth import (
    LoginInput,
    LogoutInput,
    RefreshInput,
    SignUpInput,
    ValidateTokenInput,
)
from src.domain.dtos.catalog import CategoryCreateDTO
from src.domain.exceptions import UnavailableError

pytestmark = pytest.mark.unit

SIGNUP_INPUT = SignUpInput(
    email="user@example.com", phone="+79990000000", password="S3cr3t-pass!"
)
LOGIN_INPUT = LoginInput(email="user@example.com", password="S3cr3t-pass!")
LOGOUT_INPUT = LogoutInput(session_id="session-1")
REFRESH_INPUT = RefreshInput(refresh_token="refresh-token")
VALIDATE_INPUT = ValidateTokenInput(access_token="access-token")
CATEGORY_INPUT = CategoryCreateDTO(name="clothes", parent_id=None)


async def test_signup_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await SignUpUseCase(mock_auth_gateway).execute(SIGNUP_INPUT)

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    mock_auth_gateway.sign_up.assert_awaited_once_with(SIGNUP_INPUT)


async def test_login_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await LoginUseCase(mock_auth_gateway).execute(LOGIN_INPUT)

    assert result.access_token == "access-token"
    mock_auth_gateway.login.assert_awaited_once_with(LOGIN_INPUT)


async def test_logout_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await LogoutUseCase(mock_auth_gateway).execute(LOGOUT_INPUT)

    assert result is None
    mock_auth_gateway.logout.assert_awaited_once_with(LOGOUT_INPUT)


async def test_refresh_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await RefreshUseCase(mock_auth_gateway).execute(REFRESH_INPUT)

    assert result.access_token == "access-token"
    mock_auth_gateway.refresh.assert_awaited_once_with(REFRESH_INPUT)


async def test_validate_token_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await ValidateTokenUseCase(mock_auth_gateway).execute(VALIDATE_INPUT)

    assert result.valid is True
    assert result.user_id == "user-123"
    mock_auth_gateway.validate_token.assert_awaited_once_with(VALIDATE_INPUT)


async def test_create_category_use_case_delegates_to_catalog_gateway(
    mock_catalog_gateway,
):
    result = await CreateCategoryUseCase(mock_catalog_gateway).execute(CATEGORY_INPUT)

    assert result.id == 1
    assert result.name == "category"
    mock_catalog_gateway.create_category.assert_awaited_once_with(CATEGORY_INPUT)


async def test_signup_use_case_propagates_gateway_error(mock_auth_gateway):
    mock_auth_gateway.sign_up.side_effect = UnavailableError("auth service down")
    use_case = SignUpUseCase(mock_auth_gateway)

    with pytest.raises(UnavailableError) as exc_info:
        await use_case.execute(SIGNUP_INPUT)
    assert exc_info.value.http_code == 503


async def test_login_use_case_propagates_gateway_error(mock_auth_gateway):
    mock_auth_gateway.login.side_effect = UnavailableError("auth service down")
    use_case = LoginUseCase(mock_auth_gateway)

    with pytest.raises(UnavailableError):
        await use_case.execute(LOGIN_INPUT)
