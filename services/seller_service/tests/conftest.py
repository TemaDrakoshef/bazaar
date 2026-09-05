"""Shared pytest fixtures for the seller-service test suite."""

from __future__ import annotations

import datetime
import types

import pytest


class FakeMerchantRepo:
    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_by_id(self, id_: int):
        for record in self.records:
            if record.id == id_:
                return record
        return None

    async def get_one_or_none(self, **filters):
        for record in self.records:
            if all(
                getattr(record, key, None) == value for key, value in filters.items()
            ):
                return record
        return None

    async def get_all_by_filter(self, **filters):
        return [
            record
            for record in self.records
            if all(
                getattr(record, key, None) == value for key, value in filters.items()
            )
        ]

    async def create(self, **values):
        if "id" not in values or values["id"] is None:
            values["id"] = max((r.id for r in self.records), default=0) + 1
        if "status" not in values:
            values["status"] = "ACTIVE"
        if "created_at" not in values:
            values["created_at"] = datetime.datetime.now(datetime.UTC)
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record

    async def update(self, id_: int, **values):
        for record in self.records:
            if record.id == id_:
                for key, value in values.items():
                    setattr(record, key, value)
                return record
        return None

    async def delete(self, id_: int):
        for i, record in enumerate(self.records):
            if record.id == id_:
                return self.records.pop(i)
        return None


class FakeMemberRepo:
    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_by_id(self, id_: int):
        for record in self.records:
            if record.id == id_:
                return record
        return None

    async def get_one_or_none(self, **filters):
        for record in self.records:
            if all(
                getattr(record, key, None) == value for key, value in filters.items()
            ):
                return record
        return None

    async def get_all_by_filter(self, **filters):
        return [
            record
            for record in self.records
            if all(
                getattr(record, key, None) == value for key, value in filters.items()
            )
        ]

    async def create(self, **values):
        if "id" not in values or values["id"] is None:
            values["id"] = max((r.id for r in self.records), default=0) + 1
        if "is_active" not in values:
            values["is_active"] = True
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record

    async def update(self, id_: int, **values):
        for record in self.records:
            if record.id == id_:
                for key, value in values.items():
                    setattr(record, key, value)
                return record
        return None

    async def delete(self, id_: int):
        for i, record in enumerate(self.records):
            if record.id == id_:
                return self.records.pop(i)
        return None


class FakeUnitOfWork:
    def __init__(self, merchants=(), members=()):
        self.merchant = FakeMerchantRepo()
        self.member = FakeMemberRepo()
        for merchant in merchants:
            self.merchant.records.append(merchant)
        for member in members:
            self.member.records.append(member)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        pass

    async def rollback(self):
        pass


def make_merchant(
    id_: int = 1,
    name: str = "merchant",
    inn: str = "7703456789",
    owner_user_id: str = "user-owner",
    status: str = "ACTIVE",
    created_at=None,
):
    now = created_at or datetime.datetime.now(datetime.UTC)
    return types.SimpleNamespace(
        id=id_,
        name=name,
        inn=inn,
        owner_user_id=owner_user_id,
        status=status,
        created_at=now,
    )


def make_member(
    id_: int = 1,
    merchant_id: int = 1,
    user_id: str = "user-owner",
    role: str = "OWNER",
    is_active: bool = True,
):
    return types.SimpleNamespace(
        id=id_,
        merchant_id=merchant_id,
        user_id=user_id,
        role=role,
        is_active=is_active,
    )


@pytest.fixture
def fake_uow():
    def _factory(merchants=(), members=()):
        return FakeUnitOfWork(merchants=merchants, members=members)

    return _factory
