"""Handler-level tests: successful flows, response shape, and client errors.

Uses the mocked gateway (via ``test_client``) so each handler's behaviour —
status codes, response fields, and 503 on upstream failures — can be verified
deterministically.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.domain.dtos.auth import TokenStatus
from src.domain.exceptions import UnavailableError
from src.presentation.api.dependencies import get_current_user_id
from tests.conftest import unique_email

pytestmark = pytest.mark.unit

PASSWORD = "S3cr3t-pass!"

VALID_SIGNUP = {
    "email": unique_email(),
    "phone": "+79990000000",
    "password": PASSWORD,
}


def test_signup_success_returns_201(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"] == "access-token"
    assert body["refresh_token"] == "refresh-token"
    mock_auth_gateway.sign_up.assert_awaited_once()


def test_login_success_returns_200(test_client, mock_auth_gateway):
    resp = test_client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": PASSWORD}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    mock_auth_gateway.login.assert_awaited_once()


def test_refresh_success_returns_200(test_client, mock_auth_gateway):
    resp = test_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "a-valid-refresh-token"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "access-token"
    assert body["refresh_token"] == "refresh-token"
    mock_auth_gateway.refresh.assert_awaited_once()


def test_logout_success_returns_204(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/logout", json={"session_id": "session-1"})
    assert resp.status_code == 204
    assert resp.content == b""
    mock_auth_gateway.logout.assert_awaited_once()


def test_validate_success_returns_200(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/validate", json={"access_token": "tok"})
    assert resp.status_code == 200
    assert resp.json() == {"valid": True, "user_id": "user-123", "error_message": ""}
    mock_auth_gateway.validate_token.assert_awaited_once()


def test_validate_invalid_token_returns_200_valid_false(test_client, mock_auth_gateway):
    mock_auth_gateway.validate_token.return_value = TokenStatus(
        valid=False, error_message="Invalid token"
    )
    resp = test_client.post("/api/v1/auth/validate", json={"access_token": "bad"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["error_message"] == "Invalid token"
    assert body["user_id"] is None


def test_signup_response_does_not_contain_password(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201
    raw = resp.text
    assert "password" not in raw.lower()
    assert VALID_SIGNUP["password"] not in raw


@pytest.mark.parametrize(
    "endpoint, body, mock_method",
    [
        ("/api/v1/auth/signup", VALID_SIGNUP, "sign_up"),
        (
            "/api/v1/auth/login",
            {"email": "user@example.com", "password": PASSWORD},
            "login",
        ),
        ("/api/v1/auth/refresh", {"refresh_token": "tok"}, "refresh"),
        ("/api/v1/auth/logout", {"session_id": "sid"}, "logout"),
        ("/api/v1/auth/validate", {"access_token": "tok"}, "validate_token"),
    ],
)
def test_upstream_error_maps_to_503(
    test_client, mock_auth_gateway, endpoint, body, mock_method
):
    getattr(mock_auth_gateway, mock_method).side_effect = UnavailableError(
        "upstream unavailable"
    )
    resp = test_client.post(endpoint, json=body)
    assert resp.status_code == 503


async def test_get_current_user_id_missing_header_returns_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(credentials=None, validate_token=None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


async def test_get_current_user_id_invalid_token_returns_401(mock_auth_gateway):
    mock_auth_gateway.validate_token.return_value = TokenStatus(
        valid=False, error_message="Invalid or expired token"
    )
    use_case = ValidateTokenUseCase(mock_auth_gateway)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired-token")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(credentials=creds, validate_token=use_case)
    assert exc_info.value.status_code == 401


async def test_get_current_user_id_valid_token_returns_user_id(mock_auth_gateway):
    use_case = ValidateTokenUseCase(mock_auth_gateway)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
    user_id = await get_current_user_id(credentials=creds, validate_token=use_case)
    assert user_id == "user-123"
    mock_auth_gateway.validate_token.assert_awaited_once()
