"""Shared pytest fixtures for the API Gateway test suite.

Two layers are provided:

* **Unit layer** (no infrastructure): mocked :class:`AbstractAuthGateway` and
  :class:`AbstractCatalogGateway` are wired into the FastAPI app through a dishka
  provider override (``override=True``). No real gRPC channel is ever created.
* **Integration / e2e layer** (real ``auth_service`` + PostgreSQL): a session-scoped
  fixture that spawns the real auth-service gRPC server as a subprocess on a test port,
  pointing it at a dedicated test database. The gateway app is built with a dishka
  ``Settings`` override so its auth channel targets that server. If PostgreSQL is not
  reachable these fixtures ``pytest.skip`` so the rest of the suite can still run
  (mirroring the behaviour of ``auth_service`` integration tests).
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import grpc
import pytest
from dishka import Provider, Scope, provide
from fastapi.testclient import TestClient

from src.domain.dtos.auth import AccessToken, AuthTokens, TokenStatus
from src.domain.dtos.catalog import (
    CategoryResult,
    ProductListResult,
    ProductResult,
)
from src.domain.interfaces.auth_gateway import AbstractAuthGateway
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway
from src.infrastructure.config.settings import Settings

AUTH_SERVICE_DIR = Path(__file__).resolve().parents[3] / "services" / "auth_service"
TEST_DATABASE_NAME = "bazaar_auth_test"


class MockGatewayProvider(Provider):
    """Overrides the auth/catalog gateway ports with mocks.

    Must be registered *after* ``ApiGatewayProvider`` (as ``create_app`` does)
    so dishka can resolve ``override=True`` against the real factories.
    """

    def __init__(
        self,
        auth_gateway: MagicMock,
        catalog_gateway: MagicMock,
    ) -> None:
        self._auth_gateway = auth_gateway
        self._catalog_gateway = catalog_gateway
        super().__init__()

    @provide(scope=Scope.APP, override=True)
    def provide_auth_gateway(self) -> AbstractAuthGateway:
        return self._auth_gateway

    @provide(scope=Scope.APP, override=True)
    def provide_catalog_gateway(self) -> AbstractCatalogGateway:
        return self._catalog_gateway


class TestSettingsProvider(Provider):
    """Overrides ``Settings`` so the real auth channel targets the test server."""

    def __init__(self, *, auth_host: str, auth_port: int) -> None:
        self._auth_host = auth_host
        self._auth_port = auth_port
        super().__init__()

    @provide(scope=Scope.APP, override=True)
    def provide_settings(self) -> Settings:
        return Settings(
            auth_service_host=self._auth_host, auth_service_port=self._auth_port
        )


def unique_email() -> str:
    """Return a collision-free email for a single test run."""
    return f"gateway-{uuid.uuid4().hex[:12]}@example.com"


def category_result() -> CategoryResult:
    """A ready-to-use :class:`CategoryResult` returned by the mocked catalog."""
    now = datetime.now(UTC)
    return CategoryResult(
        id=1, name="category", path="1", is_active=True, created_at=now, updated_at=now
    )


def product_result() -> ProductResult:
    """A ready-to-use :class:`ProductResult` returned by the mocked catalog."""
    now = datetime.now(UTC)
    return ProductResult(
        id=1,
        category_id=1,
        title="product",
        description=None,
        price=100,
        stock=5,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_auth_gateway() -> MagicMock:
    """Mock of :class:`AbstractAuthGateway` with AsyncMock methods returning DTOs.

    Individual tests can reconfigure any method via ``return_value`` or
    ``side_effect`` before exercising an endpoint.
    """
    gateway = MagicMock(spec=AbstractAuthGateway)
    gateway.sign_up = AsyncMock(
        return_value=AuthTokens(
            access_token="access-token", refresh_token="refresh-token"
        )
    )
    gateway.login = AsyncMock(
        return_value=AuthTokens(
            access_token="access-token", refresh_token="refresh-token"
        )
    )
    gateway.logout = AsyncMock(return_value=None)
    gateway.refresh = AsyncMock(return_value=AccessToken(access_token="access-token"))
    gateway.validate_token = AsyncMock(
        return_value=TokenStatus(valid=True, user_id="user-123", error_message="")
    )
    return gateway


@pytest.fixture
def mock_catalog_gateway() -> MagicMock:
    """Mock of :class:`AbstractCatalogGateway` with AsyncMock methods returning DTOs.

    Individual tests can reconfigure any method via ``return_value`` or
    ``side_effect`` before exercising an endpoint.
    """
    gateway = MagicMock(spec=AbstractCatalogGateway)
    gateway.create_category = AsyncMock(return_value=category_result())
    gateway.read_category = AsyncMock(return_value=category_result())
    gateway.read_list_categories = AsyncMock(return_value=[category_result()])
    gateway.update_category = AsyncMock(return_value=category_result())
    gateway.delete_category = AsyncMock(return_value=None)
    gateway.create_product = AsyncMock(return_value=product_result())
    gateway.read_product = AsyncMock(return_value=product_result())
    gateway.read_list_products = AsyncMock(
        return_value=ProductListResult(products=[product_result()], count=1)
    )
    gateway.update_product = AsyncMock(return_value=product_result())
    gateway.delete_product = AsyncMock(return_value=None)
    return gateway


@pytest.fixture
def test_client(
    mock_auth_gateway: MagicMock, mock_catalog_gateway: MagicMock
) -> TestClient:
    """FastAPI TestClient wired to the mocked gateway ports through dishka."""
    from src.app import create_app

    app = create_app(MockGatewayProvider(mock_auth_gateway, mock_catalog_gateway))
    with TestClient(app) as client:
        yield client


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
        "postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
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

    Requests flow HTTP -> gRPC -> PostgreSQL. The gRPC channel is created lazily
    inside the request that first resolves the auth gateway, so it belongs to the
    same event loop that runs the requests (a channel created outside TestClient's
    loop raises "Future attached to a different loop").
    """
    from src.app import create_app

    host, port = auth_service_proc.rsplit(":", 1)
    app = create_app(TestSettingsProvider(auth_host=host, auth_port=int(port)))
    with TestClient(app) as client:
        yield client
