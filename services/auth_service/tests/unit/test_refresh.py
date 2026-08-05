"""Unit tests for the Refresh usecase (no database, fake repositories)."""

import uuid

import pytest
from jose import jwt
from tests.conftest import make_account, make_session

from src.domain.exceptions import InvalidRefreshTokenError, SessionExpiredError
from src.usecase.base import AuthBaseUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.usecase import RefreshUsecase


async def test_refresh_success_returns_new_access_token(fake_uow):
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    refresh_token = AuthBaseUsecase.create_refresh_token(session.id)
    result = await uc.execute(RefreshRequest(refresh_token=refresh_token))

    assert uow.committed
    access_payload = AuthBaseUsecase.decode_token(result.access_token)
    assert access_payload["user_id"] == str(account.id)


async def test_refresh_invalid_token_raises(fake_uow):
    uow = fake_uow()
    uc = RefreshUsecase(uow=uow)

    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token="not-a-jwt"))


async def test_refresh_token_without_session_id_raises(fake_uow):
    uow = fake_uow()
    uc = RefreshUsecase(uow=uow)

    from src.core.settings import settings

    token = jwt.encode(
        {"exp": 9999999999}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token=token))
    assert not uow.committed


async def test_refresh_missing_session_raises(fake_uow):
    account = make_account(email="user@example.com")
    uow = fake_uow(accounts=[account])
    uc = RefreshUsecase(uow=uow)

    refresh_token = AuthBaseUsecase.create_refresh_token(uuid.uuid4())
    with pytest.raises(SessionExpiredError):
        await uc.execute(RefreshRequest(refresh_token=refresh_token))


async def test_refresh_inactive_session_raises(fake_uow):
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=False)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    refresh_token = AuthBaseUsecase.create_refresh_token(session.id)
    with pytest.raises(SessionExpiredError):
        await uc.execute(RefreshRequest(refresh_token=refresh_token))
    assert not uow.committed
