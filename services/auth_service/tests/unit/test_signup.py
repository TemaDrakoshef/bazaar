"""Unit tests for the SignUp usecase (no database, fake repositories)."""

import asyncio

import pytest
from pydantic import ValidationError as PydanticValidationError
from tests.conftest import make_account

from src.domain.exceptions import UserAlreadyExistsError, ValidationError
from src.usecase.base import AuthBaseUsecase
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.usecase import SignUpUsecase

PASSWORD = "S3cr3t-pass!"


async def _signup(uow, email: str = "user@example.com", password: str = PASSWORD):
    return await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone="+79990000000", password=password)
    )


async def test_signup_success_creates_account_and_session(fake_uow):
    uow = fake_uow()
    uc = SignUpUsecase(uow=uow)

    result = await uc.execute(
        SignUpRequest(email="new@example.com", phone="+79990000000", password=PASSWORD)
    )

    assert result.access_token
    assert result.refresh_token
    assert uow.committed

    account = uow.account.records[0]
    session = uow.session.records[0]
    assert session.user_id == account.id
    assert session.is_active is True
    assert session.refresh_token_hash == AuthBaseUsecase.hash_token(
        result.refresh_token
    )

    access_payload = AuthBaseUsecase.decode_token(
        result.access_token, expected_type="access"
    )
    assert access_payload["user_id"] == str(account.id)
    assert access_payload["session_id"] == str(session.id)

    refresh_payload = AuthBaseUsecase.decode_token(
        result.refresh_token, expected_type="refresh"
    )
    assert refresh_payload["session_id"] == str(session.id)


async def test_signup_tokens_decode_with_user_and_session(fake_uow):
    uow = fake_uow()
    uc = SignUpUsecase(uow=uow)

    result = await uc.execute(
        SignUpRequest(email="new@example.com", phone="+79990000000", password=PASSWORD)
    )

    account = uow.account.records[0]
    session = uow.session.records[0]

    access_payload = AuthBaseUsecase.decode_token(
        result.access_token, expected_type="access"
    )
    assert access_payload["user_id"] == str(account.id)
    assert access_payload["session_id"] == str(session.id)

    refresh_payload = AuthBaseUsecase.decode_token(
        result.refresh_token, expected_type="refresh"
    )
    assert refresh_payload["session_id"] == str(session.id)


async def test_signup_existing_user_raises(fake_uow):
    duplicate = make_account(email="dup@example.com")
    uow = fake_uow(accounts=[duplicate])
    uc = SignUpUsecase(uow=uow)

    with pytest.raises(UserAlreadyExistsError):
        await uc.execute(
            SignUpRequest(
                email="dup@example.com", phone="+79990000000", password=PASSWORD
            )
        )

    assert len(uow.account.records) == 1
    assert len(uow.session.records) == 0
    assert not uow.committed
    assert uow.rolled_back


async def test_signup_concurrent_same_email_single_success(fake_uow):
    """Race: two concurrent signups with the same email must yield one success."""
    uow = fake_uow()

    results = await asyncio.gather(
        _signup(uow, email="race@example.com", password=PASSWORD),
        _signup(uow, email="race@example.com", password=PASSWORD),
        return_exceptions=True,
    )

    successes = [r for r in results if not isinstance(r, BaseException)]
    failures = [r for r in results if isinstance(r, BaseException)]
    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], UserAlreadyExistsError)
    assert len(uow.account.records) == 1
    assert len(uow.session.records) == 1


async def test_signup_rolls_back_when_session_creation_fails(fake_uow):
    """If persisting the session fails, the account must not be created."""
    uow = fake_uow()
    uow.session.fail_on_create = True
    uc = SignUpUsecase(uow=uow)

    with pytest.raises(RuntimeError):
        await uc.execute(
            SignUpRequest(
                email="rollback@example.com", phone="+79990000000", password=PASSWORD
            )
        )

    assert uow.rolled_back
    assert not uow.committed
    assert len(uow.account.records) == 0
    assert len(uow.session.records) == 0


@pytest.mark.parametrize(
    "email,phone,password",
    [
        ("new@example.com", "+79990000000", ""),
        ("new@example.com", "+79990000000", "short"),
        ("new@example.com", "+79990000000", "letters000" + "A" * 100),
        ("new@example.com", "+79990000000", "allletters"),
        ("new@example.com", "12", PASSWORD),
    ],
)
async def test_signup_rejects_invalid_input(fake_uow, email, phone, password):
    uow = fake_uow()
    uc = SignUpUsecase(uow=uow)
    with pytest.raises(ValidationError):
        await uc.execute(SignUpRequest(email=email, phone=phone, password=password))
    assert not uow.committed
    assert len(uow.account.records) == 0


@pytest.mark.parametrize("email", ["not-an-email", "test@"])
async def test_signup_rejects_invalid_email_at_model_layer(email):
    """Syntactically invalid emails are rejected by the pydantic request model."""
    with pytest.raises(PydanticValidationError):
        SignUpRequest(email=email, phone="+79990000000", password=PASSWORD)
