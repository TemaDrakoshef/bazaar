"""Unit tests for the SignUp usecase (no database, fake repositories)."""

import pytest
from tests.conftest import make_account

from src.domain.exceptions import UserAlreadyExistsError
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.usecase import SignUpUsecase

PASSWORD = "S3cr3t-pass!"


async def test_signup_creates_account_and_session(fake_uow):
    uow = fake_uow()
    uc = SignUpUsecase(uow=uow)

    result = await uc.execute(
        SignUpRequest(email="new@example.com", phone="+79990000000", password=PASSWORD)
    )

    assert result.access_token
    assert result.refresh_token
    assert uow.committed
    assert len(uow.account.records) == 1
    assert len(uow.session.records) == 1

    account = uow.account.records[0]
    assert account.email == "new@example.com"
    assert account.phone == "+79990000000"
    assert account.password_hash != PASSWORD
    assert account.id

    session = uow.session.records[0]
    assert session.user_id == account.id
    assert session.is_active


async def test_signup_tokens_decode_with_user_and_session(fake_uow):
    from src.usecase.base import AuthBaseUsecase

    uow = fake_uow()
    uc = SignUpUsecase(uow=uow)

    result = await uc.execute(
        SignUpRequest(email="new@example.com", phone="+7", password=PASSWORD)
    )

    account = uow.account.records[0]
    session = uow.session.records[0]

    access_payload = AuthBaseUsecase.decode_token(result.access_token)
    assert access_payload["user_id"] == str(account.id)

    refresh_payload = AuthBaseUsecase.decode_token(result.refresh_token)
    assert refresh_payload["session_id"] == str(session.id)


async def test_signup_existing_user_raises(fake_uow):
    duplicate = make_account(email="dup@example.com")
    uow = fake_uow(accounts=[duplicate])
    uc = SignUpUsecase(uow=uow)

    with pytest.raises(UserAlreadyExistsError):
        await uc.execute(
            SignUpRequest(email="dup@example.com", phone="+7", password=PASSWORD)
        )

    assert len(uow.account.records) == 1
    assert len(uow.session.records) == 0
    assert not uow.committed
