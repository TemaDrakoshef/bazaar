"""Unit tests for the Logout usecase (no database, fake repositories)."""

import uuid

import pytest
from tests.conftest import make_account, make_session

from src.domain.exceptions import SessionNotFoundError
from src.usecase.base import AuthBaseUsecase
from src.usecase.logout.request import LogoutRequest
from src.usecase.logout.usecase import LogoutUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.usecase import ValidateTokenUsecase


async def test_logout_deactivates_session(fake_uow):
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = LogoutUsecase(uow=uow)

    await uc.execute(LogoutRequest(session_id=session.id))

    assert uow.committed
    assert session.is_active is False
    assert session.refresh_token_hash is None


async def test_logout_missing_session_raises(fake_uow):
    uow = fake_uow()
    uc = LogoutUsecase(uow=uow)

    with pytest.raises(SessionNotFoundError):
        await uc.execute(LogoutRequest(session_id=uuid.uuid4()))
    assert not uow.committed


async def test_access_token_invalid_after_logout(fake_uow):
    """An access token must no longer validate once its session is logged out."""
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    uow = fake_uow(accounts=[account], sessions=[session])

    access_token = AuthBaseUsecase.create_access_token(account.id, session.id)

    valid = await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert valid.valid is True

    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session.id))

    invalid = await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert invalid.valid is False
    assert "active" in invalid.error_message
