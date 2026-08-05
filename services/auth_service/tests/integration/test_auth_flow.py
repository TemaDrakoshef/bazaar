"""Integration tests for auth usecases against real PostgreSQL.

These tests exercise the full SQLAlchemy persistence layer: accounts and
sessions are really written to the database, passwords are really hashed, and
JWT round-trips are validated. They are skipped automatically when PostgreSQL
is not reachable (see the ``integration_engine`` fixture).
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

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
EMAIL = "integration@example.com"
PHONE = "+79990000000"


async def _create_user(uow: SQLAlchemyUnitOfWork) -> tuple[str, str]:
    """Sign up a user and return (access_token, refresh_token)."""
    result = await SignUpUsecase(uow=uow).execute(
        SignUpRequest(email=EMAIL, phone=PHONE, password=PASSWORD)
    )
    return result.access_token, result.refresh_token


async def test_signup_persists_account_and_session(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    access_token, refresh_token = await _create_user(uow)

    assert access_token
    assert refresh_token

    async with integration_session_maker() as session:
        account = (
            await session.execute(select(Account).where(Account.email == EMAIL))
        ).scalar_one()
        db_session = (
            await session.execute(select(Session).where(Session.user_id == account.id))
        ).scalar_one()

    assert account.password_hash != PASSWORD
    assert AuthBaseUsecase.verify_password(PASSWORD, account.password_hash) is True
    assert db_session.is_active is True

    assert AuthBaseUsecase.decode_token(access_token)["user_id"] == str(account.id)
    assert AuthBaseUsecase.decode_token(refresh_token)["session_id"] == str(
        db_session.id
    )


async def test_signup_duplicate_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    await _create_user(uow)

    with pytest.raises(UserAlreadyExistsError):
        await SignUpUsecase(
            uow=SQLAlchemyUnitOfWork(integration_session_maker)
        ).execute(SignUpRequest(email=EMAIL, phone=PHONE, password=PASSWORD))

    async with integration_session_maker() as session:
        accounts = (await session.execute(select(Account))).scalars().all()
    assert len(accounts) == 1


async def test_login_success_with_stored_hash(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    result = await LoginUsecase(uow=uow).execute(
        LoginRequest(email=EMAIL, password=PASSWORD)
    )
    assert result.access_token
    assert result.refresh_token

    payload = AuthBaseUsecase.decode_token(refresh_token)
    async with integration_session_maker() as session:
        db_session = (
            await session.execute(
                select(Session).where(Session.id == payload["session_id"])
            )
        ).scalar_one()
    assert db_session.is_active is True


async def test_login_wrong_password_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    await _create_user(uow)

    with pytest.raises(InvalidCredentialsError):
        await LoginUsecase(uow=uow).execute(
            LoginRequest(email=EMAIL, password="wrong-password")
        )


async def test_login_unknown_email_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    await _create_user(uow)

    with pytest.raises(InvalidCredentialsError):
        await LoginUsecase(uow=uow).execute(
            LoginRequest(email="ghost@example.com", password=PASSWORD)
        )


async def test_refresh_returns_valid_access_token(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    result = await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=refresh_token)
    )
    assert result.access_token
    payload = AuthBaseUsecase.decode_token(result.access_token)
    assert payload["user_id"]


async def test_refresh_after_logout_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    _, refresh_token = await _create_user(uow)

    session_id = AuthBaseUsecase.decode_token(refresh_token)["session_id"]
    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session_id))

    with pytest.raises(SessionExpiredError):
        await RefreshUsecase(uow=uow).execute(
            RefreshRequest(refresh_token=refresh_token)
        )


async def test_logout_unknown_session_raises(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    await _create_user(uow)

    from uuid import uuid4

    with pytest.raises(SessionNotFoundError):
        await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=uuid4()))


async def test_validate_token_after_signup(integration_session_maker):
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    access_token, _ = await _create_user(uow)

    result = await ValidateTokenUsecase().execute(
        ValidateTokenRequest(access_token=access_token)
    )
    assert result.valid is True
    assert result.user_id


async def test_full_round_trip(integration_session_maker):
    """signup -> login -> refresh -> logout -> refresh (fail)."""
    uow = SQLAlchemyUnitOfWork(integration_session_maker)
    await _create_user(uow)

    login = await LoginUsecase(uow=uow).execute(
        LoginRequest(email=EMAIL, password=PASSWORD)
    )
    refresh_resp = await RefreshUsecase(uow=uow).execute(
        RefreshRequest(refresh_token=login.refresh_token)
    )
    assert refresh_resp.access_token

    session_id = AuthBaseUsecase.decode_token(login.refresh_token)["session_id"]
    await LogoutUsecase(uow=uow).execute(LogoutRequest(session_id=session_id))

    with pytest.raises((SessionExpiredError, InvalidRefreshTokenError)):
        await RefreshUsecase(uow=uow).execute(
            RefreshRequest(refresh_token=login.refresh_token)
        )
