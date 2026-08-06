"""Unit tests for the Refresh usecase (no database, fake repositories)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt
from tests.conftest import make_account, make_session

from src.domain.exceptions import InvalidRefreshTokenError, SessionExpiredError
from src.usecase.base import AuthBaseUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.usecase import RefreshUsecase


def _session_with_token(account_id, token):
    """A session whose stored refresh-token hash matches ``token``."""
    return make_session(
        user_id=account_id,
        is_active=True,
        refresh_token_hash=AuthBaseUsecase.hash_token(token),
    )


async def test_refresh_success_returns_new_access_and_refresh_tokens(fake_uow):
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    refresh_token = AuthBaseUsecase.create_refresh_token(session.id)
    session.refresh_token_hash = AuthBaseUsecase.hash_token(refresh_token)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    result = await uc.execute(RefreshRequest(refresh_token=refresh_token))

    assert uow.committed
    assert result.refresh_token
    assert result.refresh_token != refresh_token
    access_payload = AuthBaseUsecase.decode_token(
        result.access_token, expected_type="access"
    )
    assert access_payload["user_id"] == str(account.id)
    assert session.refresh_token_hash == AuthBaseUsecase.hash_token(
        result.refresh_token
    )


async def test_refresh_token_reuse_is_rejected(fake_uow):
    """Replaying an already-consumed refresh token must fail."""
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    original_token = AuthBaseUsecase.create_refresh_token(session.id)
    session.refresh_token_hash = AuthBaseUsecase.hash_token(original_token)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    result = await uc.execute(RefreshRequest(refresh_token=original_token))

    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token=original_token))

    again = await uc.execute(RefreshRequest(refresh_token=result.refresh_token))
    assert again.access_token


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
        {"iss": settings.JWT_ISSUER, "type": "refresh", "exp": 9999999999},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token=token))
    assert not uow.committed


async def test_refresh_token_type_mismatch_raises(fake_uow):
    """An access token presented as a refresh token must be rejected."""
    account = make_account(email="user@example.com")
    session = make_session(user_id=account.id, is_active=True)
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    access_token = AuthBaseUsecase.create_access_token(account.id, session.id)
    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token=access_token))


async def test_refresh_expired_token_raises(fake_uow):
    uow = fake_uow()
    uc = RefreshUsecase(uow=uow)

    from src.core.settings import settings

    token = jwt.encode(
        {
            "iss": settings.JWT_ISSUER,
            "iat": datetime.now(UTC) - timedelta(days=8),
            "nbf": datetime.now(UTC) - timedelta(days=8),
            "exp": datetime.now(UTC) - timedelta(days=1),
            "type": "refresh",
            "session_id": str(uuid.uuid4()),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(RefreshRequest(refresh_token=token))


async def test_refresh_missing_session_raises(fake_uow):
    account = make_account(email="user@example.com")
    uow = fake_uow(accounts=[account])
    uc = RefreshUsecase(uow=uow)

    refresh_token = AuthBaseUsecase.create_refresh_token(uuid.uuid4())
    with pytest.raises(SessionExpiredError):
        await uc.execute(RefreshRequest(refresh_token=refresh_token))


async def test_refresh_inactive_session_raises(fake_uow):
    account = make_account(email="user@example.com")
    refresh_token = AuthBaseUsecase.create_refresh_token(uuid.uuid4())
    session = make_session(
        user_id=account.id,
        is_active=False,
        refresh_token_hash=AuthBaseUsecase.hash_token(refresh_token),
    )
    uow = fake_uow(accounts=[account], sessions=[session])
    uc = RefreshUsecase(uow=uow)

    with pytest.raises(SessionExpiredError):
        await uc.execute(RefreshRequest(refresh_token=refresh_token))
    assert not uow.committed
