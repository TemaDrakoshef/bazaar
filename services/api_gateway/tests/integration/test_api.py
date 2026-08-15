"""Integration tests against a real auth-service + PostgreSQL.

Drives the FastAPI gateway with mocked *nothing*: requests travel
HTTP (TestClient) -> gRPC (real AuthClient) -> auth-service -> PostgreSQL.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from jose import jwt

from tests.conftest import unique_email

pytestmark = pytest.mark.integration

TEST_JWT = {
    "secret": "test-secret-key-for-api-gateway-tests",
    "algorithm": "HS256",
    "issuer": "bazaar-auth",
}

PASSWORD = "S3cr3t-pass!"
PHONE = "+79990000000"


def _signup_payload(email: str | None = None) -> dict:
    return {"email": email or unique_email(), "phone": PHONE, "password": PASSWORD}


def _decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        TEST_JWT["secret"],
        algorithms=[TEST_JWT["algorithm"]],
        issuer=TEST_JWT["issuer"],
    )


def _session_id(refresh_token: str) -> str:
    return _decode_token(refresh_token)["session_id"]


def _expired_access_token() -> str:
    """Craft an access token whose ``exp`` is already in the past."""
    now = datetime.now(UTC)
    payload = {
        "iss": TEST_JWT["issuer"],
        "iat": now - timedelta(minutes=60),
        "nbf": now - timedelta(minutes=60),
        "exp": now - timedelta(minutes=1),
        "jti": uuid4().hex,
        "type": "access",
        "user_id": "user-123",
        "session_id": uuid4().hex,
    }
    return jwt.encode(payload, TEST_JWT["secret"], algorithm=TEST_JWT["algorithm"])


def test_signup_through_http_grpc_and_db(integration_client):
    email = unique_email()
    resp = integration_client.post("/api/v1/auth/signup", json=_signup_payload(email))
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]

    assert _session_id(body["refresh_token"])

    check = integration_client.post(
        "/api/v1/auth/validate", json={"access_token": body["access_token"]}
    )
    assert check.status_code == 200
    assert check.json()["valid"] is True


def test_login_creates_session(integration_client):
    email = unique_email()
    integration_client.post("/api/v1/auth/signup", json=_signup_payload(email))

    resp = integration_client.post(
        "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]
    assert _session_id(body["refresh_token"])


def test_login_wrong_password_returns_401(integration_client):
    email = unique_email()
    integration_client.post("/api/v1/auth/signup", json=_signup_payload(email))

    resp = integration_client.post(
        "/api/v1/auth/login", json={"email": email, "password": "WrongPass1"}
    )
    assert resp.status_code == 401


def test_refresh_rotates_and_rejects_replay(integration_client):
    email = unique_email()
    integration_client.post("/api/v1/auth/signup", json=_signup_payload(email))
    login = integration_client.post(
        "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
    ).json()
    old_refresh = login["refresh_token"]

    first = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
    )
    assert first.status_code == 200
    assert first.json()["access_token"]
    assert first.json()["access_token"] != login["access_token"]
    assert first.json()["refresh_token"]
    assert first.json()["refresh_token"] != old_refresh

    replay = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
    )
    assert replay.status_code in (401, 404)


def test_logout_deactivates_session(integration_client):
    email = unique_email()
    signup = integration_client.post(
        "/api/v1/auth/signup", json=_signup_payload(email)
    ).json()

    session_id = _session_id(signup["refresh_token"])
    logout = integration_client.post(
        "/api/v1/auth/logout", json={"session_id": session_id}
    )
    assert logout.status_code == 204

    check = integration_client.post(
        "/api/v1/auth/validate", json={"access_token": signup["access_token"]}
    )
    assert check.status_code == 200
    assert check.json()["valid"] is False


def test_concurrent_signup_same_email_single_success(integration_client):
    email = unique_email()
    payload = _signup_payload(email)

    def _signup():
        return integration_client.post("/api/v1/auth/signup", json=payload)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: _signup(), range(2)))

    statuses = sorted(r.status_code for r in results)
    assert statuses == [201, 409]


def test_expired_access_token_is_invalid(integration_client):
    expired = _expired_access_token()
    resp = integration_client.post(
        "/api/v1/auth/validate", json={"access_token": expired}
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
