"""Unit tests for the Login usecase (no database, fake repositories)."""

import pytest
from pydantic import ValidationError as PydanticValidationError
from tests.conftest import make_account, make_session

from src.domain.exceptions import InvalidCredentialsError, ValidationError
from src.usecase.base import AuthBaseUsecase
from src.usecase.login.request import LoginRequest
from src.usecase.login.usecase import LoginUsecase

PASSWORD = "S3cr3t-pass!"


def _hashed_account(**kwargs):
    """Build an account whose password_hash matches PASSWORD."""
    account = make_account(password_hash=AuthBaseUsecase.hash_password(PASSWORD))
    for key, value in kwargs.items():
        setattr(account, key, value)
    return account


async def test_login_success_returns_user_and_session_tokens(fake_uow):
    account = _hashed_account(email="user@example.com")
    session = make_session(user_id=account.id)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = LoginUsecase(uow=uow)

    result = await uc.execute(LoginRequest(email="user@example.com", password=PASSWORD))

    assert result.access_token
    assert result.refresh_token
    assert uow.committed
    assert session.is_active is True
    assert session.refresh_token_hash == AuthBaseUsecase.hash_token(
        result.refresh_token
    )

    access_payload = AuthBaseUsecase.decode_token(
        result.access_token, expected_type="access"
    )
    assert access_payload["user_id"] == str(account.id)
    assert access_payload["session_id"] == str(session.id)


async def test_login_unknown_email_raises(fake_uow):
    uow = fake_uow()
    uc = LoginUsecase(uow=uow)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginRequest(email="ghost@example.com", password=PASSWORD))
    assert not uow.committed


async def test_login_wrong_password_raises(fake_uow):
    account = _hashed_account(email="user@example.com")
    session = make_session(user_id=account.id)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = LoginUsecase(uow=uow)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginRequest(email="user@example.com", password="WrongPass1"))
    assert not uow.committed


async def test_login_inactive_account_raises(fake_uow):
    """A disabled account must not be allowed to log in."""
    account = _hashed_account(email="blocked@example.com", is_active=False)
    session = make_session(user_id=account.id)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = LoginUsecase(uow=uow)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginRequest(email="blocked@example.com", password=PASSWORD))
    assert not uow.committed


async def test_login_without_active_session_raises(fake_uow):
    account = _hashed_account(email="user@example.com")
    uow = fake_uow(accounts=[account])
    uc = LoginUsecase(uow=uow)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginRequest(email="user@example.com", password=PASSWORD))
    assert not uow.committed


async def test_login_rejects_short_password(fake_uow):
    uow = fake_uow()
    uc = LoginUsecase(uow=uow)
    with pytest.raises(ValidationError):
        await uc.execute(LoginRequest(email="user@example.com", password="short"))
    assert not uow.committed


async def test_login_rejects_invalid_email_at_model_layer():
    with pytest.raises(PydanticValidationError):
        LoginRequest(email="not-an-email", password=PASSWORD)
