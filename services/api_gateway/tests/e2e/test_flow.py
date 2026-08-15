"""End-to-end scenarios: signup -> login -> refresh -> logout.

Every request goes through the FastAPI gateway, real AuthClient, the real
auth-service gRPC server and PostgreSQL. Skips when PostgreSQL is unreachable.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from jose import jwt

from tests.conftest import unique_email

pytestmark = pytest.mark.e2e

TEST_JWT = {
    "secret": "test-secret-key-for-api-gateway-tests",
    "algorithm": "HS256",
    "issuer": "bazaar-auth",
}

PASSWORD = "S3cr3t-pass!"
PHONE = "+79990000000"


def _decode(token: str) -> dict:
    return jwt.decode(
        token,
        TEST_JWT["secret"],
        algorithms=[TEST_JWT["algorithm"]],
        issuer=TEST_JWT["issuer"],
    )


def test_full_lifecycle_signup_login_refresh_logout(integration_client):
    email = unique_email()

    signup = integration_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "phone": PHONE, "password": PASSWORD},
    )
    assert signup.status_code == 201
    signup_access = signup.json()["access_token"]
    assert _decode(signup_access)["type"] == "access"

    login = integration_client.post(
        "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
    )
    assert login.status_code == 200
    login_body = login.json()
    assert login_body["access_token"] and login_body["refresh_token"]

    refreshed = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": login_body["refresh_token"]}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    session_id = _decode(login_body["refresh_token"])["session_id"]
    logout = integration_client.post(
        "/api/v1/auth/logout", json={"session_id": session_id}
    )
    assert logout.status_code == 204


def test_refresh_rotation_chain_continues_and_rejects_replay(integration_client):
    """A correct refresh-token rotation chain can be continued indefinitely.

    login -> refresh A -> access B + refresh B
    refresh B -> access C + refresh C
    refresh A (replay) -> 401
    """
    email = unique_email()
    integration_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "phone": PHONE, "password": PASSWORD},
    )

    login = integration_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    access_a = login.json()["access_token"]
    refresh_a = login.json()["refresh_token"]
    assert _decode(access_a)["type"] == "access"
    assert _decode(refresh_a)["type"] == "refresh"

    first = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_a}
    )
    assert first.status_code == 200
    access_b = first.json()["access_token"]
    refresh_b = first.json()["refresh_token"]
    assert access_b != access_a
    assert refresh_b != refresh_a
    assert _decode(access_b)["type"] == "access"
    assert _decode(refresh_b)["type"] == "refresh"

    second = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_b}
    )
    assert second.status_code == 200
    access_c = second.json()["access_token"]
    refresh_c = second.json()["refresh_token"]
    assert access_c != access_b
    assert refresh_c != refresh_b

    third = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_c}
    )
    assert third.status_code == 200
    assert third.json()["access_token"] != access_c
    assert third.json()["refresh_token"] != refresh_c

    replay = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_a}
    )
    assert replay.status_code == 401


def test_access_token_invalid_after_logout(integration_client):
    email = unique_email()
    signup = integration_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "phone": PHONE, "password": PASSWORD},
    ).json()

    session_id = _decode(signup["refresh_token"])["session_id"]
    integration_client.post("/api/v1/auth/logout", json={"session_id": session_id})

    check = integration_client.post(
        "/api/v1/auth/validate", json={"access_token": signup["access_token"]}
    )
    assert check.status_code == 200
    assert check.json()["valid"] is False


def test_refresh_rejected_after_logout(integration_client):
    email = unique_email()
    login = integration_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "phone": PHONE, "password": PASSWORD},
    )
    session_id = _decode(login.json()["refresh_token"])["session_id"]
    integration_client.post("/api/v1/auth/logout", json={"session_id": session_id})

    resp = integration_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]}
    )
    assert resp.status_code in (401, 404)


def test_expired_token_validates_false(integration_client):
    """validate returns false for an access token whose exp has passed."""
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
    expired = jwt.encode(payload, TEST_JWT["secret"], algorithm=TEST_JWT["algorithm"])

    resp = integration_client.post(
        "/api/v1/auth/validate", json={"access_token": expired}
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
