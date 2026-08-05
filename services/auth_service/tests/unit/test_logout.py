"""Unit tests for the Logout usecase (no database, fake repositories)."""

import uuid

import pytest
from tests.conftest import make_account, make_session

from src.domain.exceptions import SessionNotFoundError
from src.usecase.logout.request import LogoutRequest
from src.usecase.logout.usecase import LogoutUsecase


async def test_logout_deactivates_session(fake_uow):
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = LogoutUsecase(uow=uow)

    await uc.execute(LogoutRequest(session_id=session.id))

    assert uow.committed
    assert session.is_active is False


async def test_logout_missing_session_raises(fake_uow):
    uow = fake_uow()
    uc = LogoutUsecase(uow=uow)

    with pytest.raises(SessionNotFoundError):
        await uc.execute(LogoutRequest(session_id=uuid.uuid4()))
    assert not uow.committed
