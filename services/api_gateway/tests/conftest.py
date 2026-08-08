"""Shared pytest fixtures for the API Gateway test suite.

Two layers are provided:

* **Unit layer** (no infrastructure): a mocked :class:`AuthClient` injected into
  the FastAPI app via dependency override, plus a ``test_client``
  (``fastapi.testclient.TestClient``) used to exercise routes and handlers in isolation.
* **Integration / e2e layer** (real ``auth_service`` + PostgreSQL): a session-scoped
  fixture that spawns the real auth-service gRPC server as a subprocess on a test port,
  pointing it at a dedicated test database. If PostgreSQL is not reachable these
  fixtures ``pytest.skip`` so the rest of the suite can still run (mirroring the
  behaviour of ``auth_service`` integration tests).
"""

from __future__ import annotations

import os
import subprocess
import sys
import types
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import grpc
import pytest
from fastapi.testclient import TestClient

from src.clients.auth_client import AuthClient
from src.generated.auth.v1 import auth_pb2

AUTH_SERVICE_DIR = Path(__file__).resolve().parents[3] / "services" / "auth_service"
TEST_DATABASE_NAME = "bazaar_auth_test"


def make_grpc_error(
    code: grpc.StatusCode, details: str = "test error"
) -> grpc.aio.AioRpcError:
    """Build an :class:`grpc.aio.AioRpcError` that the mocked client can raise."""
    return grpc.aio.AioRpcError(
        code,
        initial_metadata=None,
        trailing_metadata=None,
        details=details,
        debug_error_string=None,
    )


def unique_email() -> str:
    """Return a collision-free email for a single test run."""
    import uuid

    return f"gateway-{uuid.uuid4().hex[:12]}@example.com"


@pytest.fixture
def mock_auth_client() -> MagicMock:
    """Mock of :class:`AuthClient` with AsyncMock methods returning defaults.

    Individual tests can reconfigure any method via ``return_value`` or
    ``side_effect`` before exercising an endpoint.
    """
    client = MagicMock(spec=AuthClient)
    client.sign_up = AsyncMock(
        return_value=auth_pb2.SignUpResponse(
            access_token="access-token", refresh_token="refresh-token"
        )
    )
    client.login = AsyncMock(
        return_value=auth_pb2.LoginResponse(
            access_token="access-token", refresh_token="refresh-token"
        )
    )
    client.logout = AsyncMock(return_value=auth_pb2.LogoutResponse())
    client.refresh = AsyncMock(
        return_value=auth_pb2.RefreshResponse(access_token="access-token")
    )
    client.validate_token = AsyncMock(
        return_value=auth_pb2.ValidateTokenResponse(
            valid=True, user_id="user-123", error_message=""
        )
    )
    return client


@pytest.fixture
def mock_grpc_channel() -> MagicMock:
    """A mock gRPC channel (used only when instantiating a real client)."""
    return MagicMock()


def _app_with_client(auth_client):
    """Build the FastAPI app with ``get_auth_client`` overridden to ``auth_client``."""
    from src.app import create_app
    from src.dependencies import get_auth_client

    app = create_app()

    @asynccontextmanager
    async def _noop_lifespan(app):
        app.state.channels = types.SimpleNamespace(auth=None)
        yield

    app.router.lifespan_context = _noop_lifespan
    app.dependency_overrides[get_auth_client] = lambda: auth_client
    return app


@pytest.fixture
def test_client(mock_auth_client: MagicMock) -> TestClient:
    """FastAPI TestClient wired to the mocked auth client.

    No real gRPC channel is created (lifespan replaced), and ``get_auth_client``
    returns the mock.
    """
    app = _app_with_client(mock_auth_client)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _postgres_reachable() -> bool:
    """Best-effort check that PostgreSQL accepts TCP connections.

    ``AUTH_POSTGRES_HOST``/``AUTH_POSTGRES_PORT`` may be used to override the
    defaults, which mirror the ``auth_service`` ``.env`` (localhost:5435).
    """
    import socket

    host = os.getenv("AUTH_POSTGRES_HOST", "localhost")
    port = int(os.getenv("AUTH_POSTGRES_PORT", "5435"))
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
async def auth_service_proc() -> AsyncIterator[str]:
    """Spawn the real auth-service gRPC server as a subprocess on a test port.

    Yields ``host:port`` once the gRPC service responds, then tears the process
    down. Skips this whole layer when PostgreSQL is unreachable or env vars are
    missing (mirroring ``auth_service`` integration tests).
    """
    if not _postgres_reachable():
        pytest.skip("PostgreSQL is not reachable; skipping real auth_service tests")

    import socket
    import time

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    bootstrap = """import asyncio
import grpc
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.settings import settings
from src.persistence.models import account, session as _session  # noqa: F401
from src.persistence.models.base import Base
from src.presentation.handlers import AuthServiceHandler
from src.generated.auth.v1 import auth_pb2_grpc


async def main():
    admin = create_async_engine(
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres",
        isolation_level="AUTOCOMMIT",
    )
    async with admin.connect() as c:
        exists = await c.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": "__DB__"},
        )
        if not exists:
            await c.execute(text('CREATE DATABASE "__DB__"'))
    await admin.dispose()

    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as c:
        await c.run_sync(Base.metadata.create_all)
    await engine.dispose()

    server = grpc.aio.server()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceHandler(), server)
    server.add_insecure_port("127.0.0.1:__PORT__")
    await server.start()
    print("AUTH_SERVICE_READY", flush=True)
    await server.wait_for_termination()


asyncio.run(main())
""".replace("__DB__", TEST_DATABASE_NAME).replace("__PORT__", str(port))

    env = os.environ.copy()
    env["POSTGRES_DB"] = TEST_DATABASE_NAME
    env.update(
        {
            "JWT_SECRET": "test-secret-key-for-api-gateway-tests",
            "JWT_ALGORITHM": "HS256",
            "JWT_ISSUER": "bazaar-auth",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        }
    )

    proc = subprocess.Popen(
        [sys.executable, "-c", bootstrap],
        cwd=str(AUTH_SERVICE_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    address = f"127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                output = proc.stdout.read() if proc.stdout else ""
                pytest.skip(f"auth_service subprocess exited early: {output}")
            try:
                with grpc.insecure_channel(address) as channel:
                    grpc.channel_ready_future(channel).result(timeout=1.0)
                break
            except Exception:
                time.sleep(0.5)
        else:
            proc.kill()
            pytest.skip("auth_service subprocess did not become ready in time")
        yield address
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


@pytest.fixture
def integration_client(auth_service_proc: str) -> TestClient:
    """FastAPI TestClient backed by the real auth-service subprocess.

    Requests flow HTTP -> gRPC -> PostgreSQL. The gRPC channel is created inside
    the app's async ``lifespan`` so it belongs to the same event loop that runs
    the requests (a channel created outside TestClient's loop raises
    "Future attached to a different loop").
    """
    import grpc.aio

    from src.app import create_app

    app = create_app()

    @asynccontextmanager
    async def _real_lifespan(app):
        channel = grpc.aio.insecure_channel(auth_service_proc)
        app.state.channels = types.SimpleNamespace(auth=channel)
        yield
        await channel.close()

    app.router.lifespan_context = _real_lifespan
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
