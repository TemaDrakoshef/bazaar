"""Shared pytest fixtures for the catalog-service test suite."""

from __future__ import annotations

import types

import pytest


class FakeProductRepo:
    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_by_id(self, id_: int):
        for record in self.records:
            if record.id == id_:
                return record
        return None

    async def delete(self, id_: int):
        for i, record in enumerate(self.records):
            if record.id == id_:
                return self.records.pop(i)
        return None

    async def update(self, id_: int, **values):
        for record in self.records:
            if record.id == id_:
                for key, value in values.items():
                    setattr(record, key, value)
                return record
        return None

    async def create(self, **values):
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record


class FakeCategoryRepo:
    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_by_id(self, id_: int):
        for record in self.records:
            if record.id == id_:
                return record
        return None

    async def create(self, **values):
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record


class FakeUnitOfWork:
    def __init__(self, products=(), categories=()):
        self.product = FakeProductRepo()
        self.category = FakeCategoryRepo()
        for product in products:
            self.product.records.append(product)
        for category in categories:
            self.category.records.append(category)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        pass

    async def rollback(self):
        pass


def make_product(
    id_: int = 1,
    category_id: int = 1,
    title: str = "product",
    description: str | None = None,
    price: int = 100,
    stock: int = 5,
    is_active: bool = True,
    created_at=None,
    updated_at=None,
):
    import datetime

    now = created_at or datetime.datetime.now(datetime.UTC)
    return types.SimpleNamespace(
        id=id_,
        category_id=category_id,
        title=title,
        description=description,
        price=price,
        stock=stock,
        is_active=is_active,
        created_at=now,
        updated_at=updated_at or now,
    )


def make_category(
    id_: int = 1,
    name: str = "category",
    path: str = "1",
    is_active: bool = True,
    created_at=None,
    updated_at=None,
):
    import datetime

    now = created_at or datetime.datetime.now(datetime.UTC)
    return types.SimpleNamespace(
        id=id_,
        name=name,
        path=path,
        is_active=is_active,
        created_at=now,
        updated_at=updated_at or now,
    )


@pytest.fixture
def fake_uow():
    def _factory(products=(), categories=()):
        return FakeUnitOfWork(products=products, categories=categories)

    return _factory
