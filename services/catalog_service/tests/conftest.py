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
                getattr(record, key, None) == value for key, value in filters.items()
            )
        ]

    async def get_page(self, offset: int, limit: int, **filters):
        matched = await self.get_all_by_filter(**filters)
        return matched[offset : offset + limit]

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
                getattr(record, key, None) == value for key, value in filters.items()
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


class FakeMediaRepo:
    def __init__(self) -> None:
        self.records: list[types.SimpleNamespace] = []

    async def get_by_id(self, id_: int):
        for record in self.records:
            if record.id == id_:
                return record
        return None

    async def list_by_product(self, product_id: int):
        return sorted(
            [r for r in self.records if r.product_id == product_id],
            key=lambda r: (r.position, r.id),
        )

    async def list_by_products(self, product_ids: list[int]):
        grouped: dict[int, list] = {}
        for record in self.records:
            if record.product_id in product_ids:
                grouped.setdefault(record.product_id, []).append(record)
        for records in grouped.values():
            records.sort(key=lambda r: (r.position, r.id))
        return grouped

    async def list_by_ids(self, media_ids: list[int]):
        return [r for r in self.records if r.id in media_ids]

    async def next_position(self, product_id: int) -> int:
        positions = [r.position for r in self.records if r.product_id == product_id]
        return (max(positions) if positions else -1) + 1

    async def has_video(self, product_id: int) -> bool:
        return any(
            r.product_id == product_id and r.media_type == "VIDEO" for r in self.records
        )

    async def create(self, **values):
        if "id" not in values or values["id"] is None:
            values["id"] = max((r.id for r in self.records), default=0) + 1
        if "position" not in values:
            values["position"] = 0
        record = types.SimpleNamespace(**values)
        self.records.append(record)
        return record

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

    async def update_positions(self, updates: list[tuple[int, int]]) -> None:
        for media_id, position in updates:
            for record in self.records:
                if record.id == media_id:
                    record.position = position
                    break


class FakeUnitOfWork:
    def __init__(self, products=(), categories=(), media=()):
        self.product = FakeProductRepo()
        self.category = FakeCategoryRepo()
        self.media = FakeMediaRepo()
        for product in products:
            self.product.records.append(product)
        for category in categories:
            self.category.records.append(category)
        for item in media:
            self.media.records.append(item)

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
    merchant_id: int = 1,
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
        merchant_id=merchant_id,
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
    def _factory(products=(), categories=(), media=()):
        return FakeUnitOfWork(products=products, categories=categories, media=media)

    return _factory


class FakeStorageService:
    def __init__(self) -> None:
        self.bucket = "bazaar-media"
        self.presigned: list[tuple[str, str]] = []
        self.deleted: list[str] = []

    async def generate_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 600
    ) -> str:
        self.presigned.append((key, content_type))
        return f"https://minio.local/presign/{key}"

    async def delete_object(self, key: str) -> None:
        self.deleted.append(key)

    def public_url(self, key: str) -> str:
        return f"http://localhost:9000/bazaar-media/{key}"


@pytest.fixture
def fake_storage():
    return FakeStorageService()


def make_media(
    id_: int = 1,
    product_id: int = 1,
    media_type: str = "IMAGE",
    storage_key: str = "products/1/images/img.jpg",
    url: str = "http://localhost:9000/bazaar-media/products/1/images/img.jpg",
    position: int = 0,
    width: int | None = None,
    height: int | None = None,
    duration_seconds: int | None = None,
    file_size: int = 1024,
    created_at=None,
):
    import datetime

    now = created_at or datetime.datetime.now(datetime.UTC)
    return types.SimpleNamespace(
        id=id_,
        product_id=product_id,
        media_type=media_type,
        storage_key=storage_key,
        url=url,
        position=position,
        width=width,
        height=height,
        duration_seconds=duration_seconds,
        file_size=file_size,
        created_at=now,
    )
