"""Handler-level tests: successful flows, response shape, and client errors.

Uses the mocked :class:`AuthClient` (via ``test_client``) so each handler's
behaviour — status codes, response fields, and 503 on gRPC client failures — can
be verified deterministically.
"""

from __future__ import annotations

import grpc
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from tests.conftest import make_grpc_error, unique_email

pytestmark = pytest.mark.unit

PASSWORD = "S3cr3t-pass!"

VALID_SIGNUP = {
    "email": unique_email(),
    "phone": "+79990000000",
    "password": PASSWORD,
}


def test_signup_success_returns_201(test_client, mock_auth_client):
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"] == "access-token"
    assert body["refresh_token"] == "refresh-token"
    mock_auth_client.sign_up.assert_awaited_once()


def test_login_success_returns_200(test_client, mock_auth_client):
    resp = test_client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": PASSWORD}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    mock_auth_client.login.assert_awaited_once()


def test_refresh_success_returns_200(test_client, mock_auth_client):
    resp = test_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "a-valid-refresh-token"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"access_token": "access-token"}
    mock_auth_client.refresh.assert_awaited_once()


def test_logout_success_returns_204(test_client, mock_auth_client):
    resp = test_client.post("/api/v1/auth/logout", json={"session_id": "session-1"})
    assert resp.status_code == 204
    assert resp.content == b""
    mock_auth_client.logout.assert_awaited_once()


def test_validate_success_returns_200(test_client, mock_auth_client):
    resp = test_client.post("/api/v1/auth/validate", json={"access_token": "tok"})
    assert resp.status_code == 200
    assert resp.json() == {"valid": True, "user_id": "user-123", "error_message": ""}
    mock_auth_client.validate_token.assert_awaited_once()


def test_validate_invalid_token_returns_200_valid_false(test_client, mock_auth_client):
    from src.generated.auth.v1 import auth_pb2

    mock_auth_client.validate_token.return_value = auth_pb2.ValidateTokenResponse(
        valid=False, error_message="Invalid token"
    )
    resp = test_client.post("/api/v1/auth/validate", json={"access_token": "bad"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["error_message"] == "Invalid token"
    assert body["user_id"] is None


def test_signup_response_does_not_contain_password(test_client, mock_auth_client):
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201
    raw = resp.text
    assert "password" not in raw.lower()
    assert VALID_SIGNUP["password"] not in raw


@pytest.mark.parametrize(
    "endpoint, body, mock_method, error_code",
    [
        ("/api/v1/auth/signup", VALID_SIGNUP, "sign_up", grpc.StatusCode.UNAVAILABLE),
        (
            "/api/v1/auth/login",
            {"email": "user@example.com", "password": PASSWORD},
            "login",
            grpc.StatusCode.DEADLINE_EXCEEDED,
        ),
        (
            "/api/v1/auth/refresh",
            {"refresh_token": "tok"},
            "refresh",
            grpc.StatusCode.UNAVAILABLE,
        ),
        (
            "/api/v1/auth/logout",
            {"session_id": "sid"},
            "logout",
            grpc.StatusCode.DEADLINE_EXCEEDED,
        ),
        (
            "/api/v1/auth/validate",
            {"access_token": "tok"},
            "validate_token",
            grpc.StatusCode.UNAVAILABLE,
        ),
    ],
)
def test_grpc_client_error_maps_to_503(
    test_client, mock_auth_client, endpoint, body, mock_method, error_code
):
    getattr(mock_auth_client, mock_method).side_effect = make_grpc_error(
        error_code, "upstream unavailable"
    )
    resp = test_client.post(endpoint, json=body)
    assert resp.status_code == 503


async def test_get_current_user_id_missing_header_returns_401():
    from src.dependencies import get_current_user_id

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(credentials=None, auth_client=None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


async def test_get_current_user_id_invalid_token_returns_401(mock_auth_client):
    from src.dependencies import get_current_user_id
    from src.generated.auth.v1 import auth_pb2

    mock_auth_client.validate_token.return_value = auth_pb2.ValidateTokenResponse(
        valid=False, error_message="Invalid or expired token"
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired-token")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(credentials=creds, auth_client=mock_auth_client)
    assert exc_info.value.status_code == 401


async def test_get_current_user_id_valid_token_returns_user_id(mock_auth_client):
    from src.dependencies import get_current_user_id

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
    user_id = await get_current_user_id(credentials=creds, auth_client=mock_auth_client)
    assert user_id == "user-123"
    mock_auth_client.validate_token.assert_awaited_once()
