"""Unit tests for the AuthBaseUsecase helpers (bcrypt + JWT)."""

import uuid

import pytest
from jose import JWTError

from src.core.settings import settings
from src.usecase.base import AuthBaseUsecase


async def test_hash_and_verify_password():
    hashed = AuthBaseUsecase.hash_password("my-password")
    assert hashed != "my-password"
    assert AuthBaseUsecase.verify_password("my-password", hashed) is True
    assert AuthBaseUsecase.verify_password("wrong", hashed) is False


async def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id)
    payload = AuthBaseUsecase.decode_token(token)
    assert payload["user_id"] == str(user_id)
    assert "exp" in payload


async def test_refresh_token_roundtrip():
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_refresh_token(session_id)
    payload = AuthBaseUsecase.decode_token(token)
    assert payload["session_id"] == str(session_id)
    assert "exp" in payload


async def test_decode_token_rejects_tampered():
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id)
    tampered = token[:-3] + ("abc" if not token.endswith("abc") else "def")
    with pytest.raises(JWTError):
        AuthBaseUsecase.decode_token(tampered)


async def test_decode_token_wrong_secret():
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id)
    with pytest.raises(JWTError):
        from jose import jwt

        jwt.decode(token, "some-other-secret", algorithms=[settings.JWT_ALGORITHM])
