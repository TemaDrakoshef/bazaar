"""Route-level tests: request validation and error mapping.

These tests exercise the FastAPI routing layer with a mocked auth gateway, so
validation (Pydantic schemas) and the ``ApplicationError`` -> HTTP mapping are
covered without any infrastructure.
"""

from __future__ import annotations

import pytest

from src.domain.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    UnauthenticatedError,
    ValidationError,
)
from tests.conftest import unique_email

pytestmark = pytest.mark.unit

VALID_SIGNUP = {
    "email": unique_email(),
    "phone": "+79990000000",
    "password": "S3cr3t-pass!",
}


def test_signup_invalid_email_returns_422(test_client, mock_auth_gateway):
    payload = {**VALID_SIGNUP, "email": "not-an-email"}
    resp = test_client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422
    mock_auth_gateway.sign_up.assert_not_awaited()


def test_signup_empty_password_returns_422(test_client, mock_auth_gateway):
    payload = {**VALID_SIGNUP, "password": ""}
    resp = test_client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422
    mock_auth_gateway.sign_up.assert_not_awaited()


def test_signup_short_password_returns_422(test_client, mock_auth_gateway):
    payload = {**VALID_SIGNUP, "password": "short"}
    resp = test_client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422
    mock_auth_gateway.sign_up.assert_not_awaited()


def test_signup_short_phone_returns_422(test_client, mock_auth_gateway):
    payload = {**VALID_SIGNUP, "phone": "12"}
    resp = test_client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422
    mock_auth_gateway.sign_up.assert_not_awaited()


def test_login_missing_email_returns_422(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/login", json={"password": "S3cr3t-pass!"})
    assert resp.status_code == 422
    mock_auth_gateway.login.assert_not_awaited()


def test_login_missing_password_returns_422(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/login", json={"email": "user@example.com"})
    assert resp.status_code == 422
    mock_auth_gateway.login.assert_not_awaited()


def test_refresh_missing_refresh_token_returns_422(test_client, mock_auth_gateway):
    resp = test_client.post("/api/v1/auth/refresh", json={})
    assert resp.status_code == 422
    mock_auth_gateway.refresh.assert_not_awaited()


def test_signup_already_exists_maps_to_409(test_client, mock_auth_gateway):
    mock_auth_gateway.sign_up.side_effect = ConflictError("user already exists")
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_login_invalid_credentials_maps_to_401(test_client, mock_auth_gateway):
    mock_auth_gateway.login.side_effect = UnauthenticatedError("invalid credentials")
    resp = test_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "S3cr3t-pass!"},
    )
    assert resp.status_code == 401


def test_logout_session_not_found_maps_to_404(test_client, mock_auth_gateway):
    mock_auth_gateway.logout.side_effect = NotFoundError("session not found")
    resp = test_client.post("/api/v1/auth/logout", json={"session_id": "missing-id"})
    assert resp.status_code == 404


def test_refresh_token_expired_maps_to_401(test_client, mock_auth_gateway):
    mock_auth_gateway.refresh.side_effect = UnauthenticatedError("token expired")
    resp = test_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "expired-token"}
    )
    assert resp.status_code == 401


def test_signup_validation_error_maps_to_422(test_client, mock_auth_gateway):
    mock_auth_gateway.sign_up.side_effect = ValidationError(
        "email is not a valid address"
    )
    resp = test_client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 422


def test_validate_permission_denied_maps_to_403(test_client, mock_auth_gateway):
    mock_auth_gateway.validate_token.side_effect = PermissionDeniedError(
        "access denied"
    )
    resp = test_client.post("/api/v1/auth/validate", json={"access_token": "tok"})
    assert resp.status_code == 403
