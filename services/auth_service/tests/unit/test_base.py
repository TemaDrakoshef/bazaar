"""Unit tests for the AuthBaseUsecase helpers (bcrypt + JWT)."""

import time
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import JWTError, jwt

from src.core.settings import settings
from src.usecase.base import AuthBaseUsecase


async def test_hash_and_verify_password():
    hashed = AuthBaseUsecase.hash_password("my-password")
    assert hashed != "my-password"
    assert AuthBaseUsecase.verify_password("my-password", hashed) is True
    assert AuthBaseUsecase.verify_password("wrong", hashed) is False


async def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, session_id)
    payload = AuthBaseUsecase.decode_token(token, expected_type="access")
    assert payload["user_id"] == str(user_id)
    assert payload["session_id"] == str(session_id)
    assert payload["iss"] == settings.JWT_ISSUER
    assert payload["type"] == "access"


async def test_refresh_token_roundtrip():
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_refresh_token(session_id)
    payload = AuthBaseUsecase.decode_token(token, expected_type="refresh")
    assert payload["session_id"] == str(session_id)
    assert payload["iss"] == settings.JWT_ISSUER
    assert payload["type"] == "refresh"


async def test_tokens_carry_lifecycle_claims():
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(uuid.uuid4(), session_id)
    payload = AuthBaseUsecase.decode_token(token, expected_type="access")
    now = time.time()
    assert payload["iat"] <= payload["nbf"] + 1
    assert payload["exp"] > now
    assert "nbf" in payload


async def test_decode_requires_expected_type():
    session_id = uuid.uuid4()
    access = AuthBaseUsecase.create_access_token(uuid.uuid4(), session_id)
    refresh = AuthBaseUsecase.create_refresh_token(session_id)
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(access, expected_type="refresh")
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(refresh, expected_type="access")


async def test_decode_expired_access_token_raises():
    session_id = uuid.uuid4()
    token = jwt.encode(
        {
            "iss": settings.JWT_ISSUER,
            "iat": datetime.now(UTC) - timedelta(minutes=40),
            "nbf": datetime.now(UTC) - timedelta(minutes=40),
            "exp": datetime.now(UTC) - timedelta(minutes=10),
            "type": "access",
            "user_id": str(uuid.uuid4()),
            "session_id": str(session_id),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(token, expected_type="access")


async def test_decode_expired_refresh_token_raises():
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
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(token, expected_type="refresh")


async def test_decode_token_rejects_tampered():
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, uuid.uuid4())
    tampered = token[:-3] + ("abc" if not token.endswith("abc") else "def")
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(tampered)


async def test_decode_token_wrong_secret():
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, uuid.uuid4())
    with pytest.raises(JWTError):
        jwt.decode(token, "some-other-secret", algorithms=[settings.JWT_ALGORITHM])


async def test_hash_token_is_stable_and_deterministic():
    token = "some-refresh-token"
    assert AuthBaseUsecase.hash_token(token) == AuthBaseUsecase.hash_token(token)
    assert AuthBaseUsecase.hash_token(token) != token
