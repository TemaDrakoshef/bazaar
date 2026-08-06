from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select
from tests.conftest import unique_email

from src.domain.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    SessionExpiredError,
    SessionNotFoundError,
    UserAlreadyExistsError,
)
from src.persistence.models.account import Account
from src.persistence.models.session import Session
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.login.request import LoginRequest
from src.usecase.login.usecase import LoginUsecase
from src.usecase.logout.request import LogoutRequest
from src.usecase.logout.usecase import LogoutUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.usecase import RefreshUsecase
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.usecase import SignUpUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.usecase import ValidateTokenUsecase

PASSWORD = "S3cr3t-pass!"
PHONE = "+79990000000"


async def _create_user(uow: SQLAlchemyUnitOfWork) -> tuple[str, str]:
    """Sign up a fresh user and return (access_token, refresh_token)."""
    result = await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=unique_email(), phone=PHONE, password=PASSWORD)
    )
    return result.access_token, result.refresh_token


async def test_signup_persists_account_and_session(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    result = await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    assert result.access_token
    assert result.refresh_token

    async with integration_session_maker() as session:
        account = (
            await session.execute(select(Account).where(Account.email == email))
        ).scalar_one()
        db_session = (
            await session.execute(select(Session).where(Session.user_id == account.id))
        ).scalar_one()

    assert account.password_hash != PASSWORD
    assert AuthBaseUsecase.verify_password(PASSWORD, account.password_hash) is True
    assert db_session.is_active is True
    assert db_session.refresh_token_hash == AuthBaseUsecase.hash_token(
        result.refresh_token
    )

    assert AuthBaseUsecase.decode_token(result.access_token, expected_type="access")[
        "user_id"
    ] == str(account.id)
    assert AuthBaseUsecase.decode_token(result.refresh_token, expected_type="refresh")[
        "session_id"
    ] == str(db_session.id)


async def test_signup_duplicate_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    with pytest.raises(UserAlreadyExistsError):
        await SignUpUsecase(
            uow=SQLAlchemyUnitOfWork(integration_session_maker)
        ).execute(SignUpRequest(email=email, phone=PHONE, password=PASSWORD))

    async with integration_session_maker() as session:
        accounts = (await session.execute(select(Account))).scalars().all()
    assert len(accounts) == 1


async def test_signup_concurrent_same_email_single_success(integration_session_maker):
    """Two concurrent signups with the same email: exactly one must succeed."""
    email = unique_email()

    async def _signup():
        return await SignUpUsecase(
            uow=SQLAlchemyUnitOfWork(integration_session_maker)
        ).execute(SignUpRequest(email=email, phone=PHONE, password=PASSWORD))

    results = await asyncio.gather(_signup(), _signup(), return_exceptions=True)

    successes = [r for r in results if not isinstance(r, BaseException)]
    failures = [r for r in results if isinstance(r, BaseException)]
    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], UserAlreadyExistsError)

    async with integration_session_maker() as session:
        accounts = (await session.execute(select(Account))).scalars().all()
    assert len(accounts) == 1


async def test_login_success_with_stored_hash(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    result = await LoginUsecase(uow=uow).execute(
        LoginRequest(email=email, password=PASSWORD)
    )
    assert result.access_token
    assert result.refresh_token

    payload = AuthBaseUsecase.decode_token(
        result.refresh_token, expected_type="refresh"
    )
    async with integration_session_maker() as session:
        db_session = (
            await session.execute(
                select(Session).where(Session.id == payload["session_id"])
            )
        ).scalar_one()
    assert db_session.is_active is True
    assert db_session.refresh_token_hash == AuthBaseUsecase.hash_token(
        result.refresh_token
    )


async def test_login_inactive_account_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    async with integration_session_maker() as session:
        account = (
            await session.execute(select(Account).where(Account.email == email))
        ).scalar_one()
        account.is_active = False
        await session.commit()

    with pytest.raises(InvalidCredentialsError):
        await LoginUsecase(uow=uow).execute(
            LoginRequest(email=email, password=PASSWORD)
        )


async def test_login_wrong_password_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    with pytest.raises(InvalidCredentialsError):
        await LoginUsecase(uow=uow).execute(
            LoginRequest(email=email, password="WrongPass1")
        )


async def test_login_unknown_email_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    with pytest.raises(InvalidCredentialsError):
        await LoginUsecase(uow=uow).execute(
            LoginRequest(email=unique_email(), password=PASSWORD)
        )


async def test_refresh_rotates_tokens(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    first = await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=refresh_token)
    )
    assert first.access_token
    assert first.refresh_token
    assert first.refresh_token != refresh_token

    payload = AuthBaseUsecase.decode_token(first.access_token, expected_type="access")
    assert payload["user_id"]


async def test_refresh_reuse_is_rejected(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    first = await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=refresh_token)
    )

    with pytest.raises(InvalidRefreshTokenError):
        await RefreshUsecase(uow=uow).execute(
            RefreshRequest(refresh_token=refresh_token)
        )

    await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=first.refresh_token)
    )


async def test_refresh_after_logout_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    session_id = AuthBaseUsecase.decode_token(refresh_token, expected_type="refresh")[
        "session_id"
    ]
    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session_id))

    with pytest.raises(SessionExpiredError):
        await RefreshUsecase(uow=uow).execute(
            RefreshRequest(refresh_token=refresh_token)
        )


async def test_access_token_invalid_after_logout(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    access_token, _ = await _create_user(uow)

    before = await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert before.valid is True

    session_id = AuthBaseUsecase.decode_token(access_token, expected_type="access")[
        "session_id"
    ]
    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session_id))

    after = await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert after.valid is False


async def test_logout_unknown_session_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)

    from uuid import uuid4

    with pytest.raises(SessionNotFoundError):
        await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=uuid4()))


async def test_validate_token_after_signup(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    access_token, _ = await _create_user(uow)

    result = await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert result.valid is True
    assert result.user_id


async def test_full_round_trip(integration_session_maker):
    """signup -> login -> refresh -> logout -> refresh (fail)."""
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    email = unique_email()
    await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=email, phone=PHONE, password=PASSWORD)
    )

    login = await LoginUsecase(uow=uow).execute(
        LoginRequest(email=email, password=PASSWORD)
    )
    refresh_resp = await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=login.refresh_token)
    )
    assert refresh_resp.access_token

    session_id = AuthBaseUsecase.decode_token(
        login.refresh_token, expected_type="refresh"
    )["session_id"]
    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session_id))

    with pytest.raises((SessionExpiredError, InvalidRefreshTokenError)):
        await RefreshUsecase(uow=uow).execute(
            RefreshRequest(refresh_token=login.refresh_token)
        )
