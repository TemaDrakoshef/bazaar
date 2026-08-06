"""Shared pytest fixtures for the auth-service test suite.

Two layers are provided:

* **Unit layer** (no database): fake repositories / fake unit-of-work used to
  exercise usecase logic and gRPC handlers in isolation.
* **Integration layer** (real PostgreSQL): an async engine + session maker bound
  to a dedicated test database that is created on demand. If PostgreSQL is not
  reachable these fixtures ``pytest.skip`` so the rest of the suite can still run.
"""

from __future__ import annotations

import types
import uuid
from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.core.settings import settings


class FakeAccountRepo:
    """In-memory repository exposing the account methods used by the usecases."""

    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_one_or_none(self, **filters):
        for record in self.records:
            if all(getattr(record, key) == value for key, value in filters.items()):
                return record
        return None

    async def create(self, **values):
        values.setdefault("is_active", True)
        if any(r.email == values.get("email") for r in self.records):
            from src.domain.exceptions import UserAlreadyExistsError

            raise UserAlreadyExistsError()
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record


class FakeSessionRepo:
    """In-memory repository exposing the session methods used by the usecases."""

    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []
        self.fail_on_create = False

    async def get_one_or_none(self, **filters):
        for record in self.records:
            if all(getattr(record, key) == value for key, value in filters.items()):
                return record
        return None

    async def get_by_id(self, id_: UUID):
        for record in self.records:
            if str(record.id) == str(id_):
                return record
        return None

    async def create(self, **values):
        if self.fail_on_create:
            raise RuntimeError("session create failed")
        values.setdefault("is_active", True)
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record

    async def update(self, id_: UUID, **values):
        for record in self.records:
            if str(record.id) == str(id_):
                for key, value in values.items():
                    setattr(record, key, value)
                return record
        return None


class FakeUnitOfWork:
    """In-memory unit of work used to drive usecases without a database.

    ``commit`` records the fact of a commit; ``rollback`` restores the
    repositories to the state captured when the unit of work was entered, so
    errors mid-transaction behave like a real database rollback.
    """

    def __init__(self, accounts=(), sessions=()):
        self.account = FakeAccountRepo()
        self.session = FakeSessionRepo()
        for account in accounts:
            self.account.records.append(account)
        for session in sessions:
            self.session.records.append(session)
        self.committed = False
        self.rolled_back = False
        self._snapshots: tuple[list, list] | None = None

    def _snapshot(self):
        return (list(self.account.records), list(self.session.records))

    async def __aenter__(self):
        self.committed = False
        self.rolled_back = False
        self._snapshots = self._snapshot()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            await self.rollback()
        return False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        if self._snapshots is not None:
            self.account.records, self.session.records = self._snapshots
        self.rolled_back = True


def make_account(
    email: str = "user@example.com",
    phone: str = "+79990000000",
    password_hash: str = "",
    is_active: bool = True,
    id_: UUID | None = None,
) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        id=id_ or uuid.uuid4(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        is_active=is_active,
    )


def make_session(
    user_id: UUID,
    is_active: bool = True,
    id_: UUID | None = None,
    refresh_token_hash: str | None = None,
) -> types.SimpleNamespace:
    import datetime

    return types.SimpleNamespace(
        id=id_ or uuid.uuid4(),
        user_id=user_id,
        is_active=is_active,
        refresh_token_hash=refresh_token_hash,
        last_active_at=datetime.datetime.now(),
    )


def unique_email() -> str:
    """Return a collision-free email for a single test run."""
    return f"user-{uuid.uuid4().hex[:12]}@example.com"


def unique_phone() -> str:
    return f"+7999{uuid.uuid4().hex[:9]}"


@pytest.fixture
def fake_uow():
    """Thin wrapper so tests can build a pre-seeded FakeUnitOfWork."""

    def _factory(accounts=(), sessions=()):
        return FakeUnitOfWork(accounts=accounts, sessions=sessions)

    return _factory


@pytest.fixture
def create_account():
    """Factory helper building an account with a known (hashed) password."""

    def _factory(email=None, *, is_active: bool = True, password: str = "S3cr3t-pass!"):
        from src.usecase.base import AuthBaseUsecase

        return make_account(
            email=email or unique_email(),
            password_hash=AuthBaseUsecase.hash_password(password),
            is_active=is_active,
        )

    return _factory


TEST_DATABASE_NAME = "bazaar_auth_test"


def _admin_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )


def _test_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DATABASE_NAME}"
    )


@pytest.fixture(scope="session")
async def integration_engine() -> AsyncIterator[AsyncEngine]:
    """Create (if needed) the test database and return an engine bound to it."""
    from src.persistence.models import account as _account  # noqa: F401
    from src.persistence.models import session as _session  # noqa: F401
    from src.persistence.models.base import Base

    admin_engine = create_async_engine(_admin_url(), isolation_level="AUTOCOMMIT")
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": TEST_DATABASE_NAME},
            )
            if not exists:
                db_name = TEST_DATABASE_NAME.replace('"', '""')
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    except Exception as exc:
        await admin_engine.dispose()
        pytest.skip(f"PostgreSQL is not reachable: {exc}")
    await admin_engine.dispose()

    engine = create_async_engine(_test_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def integration_session_maker(
    integration_engine: AsyncEngine,
) -> async_sessionmaker:
    maker = async_sessionmaker(integration_engine, expire_on_commit=False)
    async with integration_engine.begin() as conn:
        await conn.execute(text("TRUNCATE sessions, accounts RESTART IDENTITY CASCADE"))
    return maker
