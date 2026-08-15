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

    async def get_all_by_filter(self, **filters):
        return [
            record
            for record in self.records
            if all(
                getattr(record, key, None) == value
                for key, value in filters.items()
            )
        ]

    async def count(self, **filters) -> int:
        return len(await self.get_all_by_filter(**filters))

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

    async def get_all_by_filter(self, **filters):
        return [
            record
            for record in self.records
            if all(
                getattr(record, key, None) == value
                for key, value in filters.items()
            )
        ]

    async def count(self, **filters) -> int:
        return len(await self.get_all_by_filter(**filters))

    async def get_descendants(self, path: str):
        return [
            record
            for record in self.records
            if str(record.path) == path or str(record.path).startswith(f"{path}.")
        ]

    async def create(self, **values):
        if "id" not in values or values["id"] is None:
            values["id"] = max((r.id for r in self.records), default=0) + 1
        if "is_active" not in values:
            values["is_active"] = True
        if "created_at" not in values:
            import datetime

            values["created_at"] = datetime.datetime.now(datetime.UTC)
        if "updated_at" not in values:
            values["updated_at"] = values["created_at"]
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
    parent_id: int | None = None,
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
        parent_id=parent_id,
        is_active=is_active,
        created_at=now,
        updated_at=updated_at or now,
    )


@pytest.fixture
def fake_uow():
    def _factory(products=(), categories=()):
        return FakeUnitOfWork(products=products, categories=categories)

    return _factory
