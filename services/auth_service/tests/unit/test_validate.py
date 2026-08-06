"""Unit tests for the ValidateToken usecase (no database)."""

import uuid

from jose import jwt

from src.core.settings import settings
from src.usecase.base import AuthBaseUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.usecase import ValidateTokenUsecase


async def _validate(token, uow=None):
    return await ValidateTokenUsecase(uow=uow).execute(
        ValidateTokenRequest(access_token=token)
    )


async def test_validate_valid_token():
    token = AuthBaseUsecase.create_access_token(uuid.uuid4(), uuid.uuid4())
    result = await _validate(token)
    assert result.valid is True
    assert result.user_id


async def test_validate_invalid_token():
    result = await _validate("garbage.token.value")
    assert result.valid is False
    assert result.user_id is None
    assert result.error_message == "Invalid token"


async def test_validate_token_without_user_id():
    token = jwt.encode(
        {"iss": settings.JWT_ISSUER, "type": "access", "exp": 9999999999},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    result = await _validate(token)
    assert result.valid is False
    assert result.error_message == "Invalid token"


async def test_validate_expired_access_token_is_invalid():
    token = AuthBaseUsecase.create_access_token(uuid.uuid4(), uuid.uuid4())
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    payload = {**payload, "exp": 1}
    expired = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    result = await _validate(expired)
    assert result.valid is False
    assert result.error_message == "Invalid token"


async def test_validate_rejects_refresh_token_as_access():
    refresh = AuthBaseUsecase.create_refresh_token(uuid.uuid4())
    result = await _validate(refresh)
    assert result.valid is False


async def test_validate_active_session_returns_valid(fake_uow):
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, session_id)
    uow = fake_uow(sessions=[_ns(id=session_id, user_id=user_id, is_active=True)])
    result = await _validate(token, uow=uow)
    assert result.valid is True
    assert result.user_id == str(user_id)


async def test_validate_inactive_session_is_invalid(fake_uow):
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, session_id)
    uow = fake_uow(sessions=[_ns(id=session_id, user_id=user_id, is_active=False)])
    result = await _validate(token, uow=uow)
    assert result.valid is False
    assert "active" in result.error_message


async def test_validate_missing_session_is_invalid(fake_uow):
    user_id = uuid.uuid4()
    token = AuthBaseUsecase.create_access_token(user_id, uuid.uuid4())
    uow = fake_uow()
    result = await _validate(token, uow=uow)
    assert result.valid is False


def _ns(**kwargs):
    import types

    return types.SimpleNamespace(**kwargs)
