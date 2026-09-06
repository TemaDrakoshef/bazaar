"""Unit tests for the product-media use cases."""

from __future__ import annotations

import pytest

from src.application.use_cases.confirm_media_upload import ConfirmMediaUploadUseCase
from src.application.use_cases.delete_media import DeleteMediaUseCase
from src.application.use_cases.get_media_upload_url import GetMediaUploadUrlUseCase
from src.application.use_cases.reorder_media import ReorderMediaUseCase
from src.domain.dtos.media import (
    ConfirmMediaUploadRequest,
    DeleteMediaRequest,
    MediaUploadUrlRequest,
    ReorderMediaItemDTO,
    ReorderMediaRequest,
)
from src.domain.entities.media import MediaType
from src.domain.exceptions import (
    AccessDeniedError,
    MediaNotFoundError,
    MediaValidationError,
    ProductNotFoundError,
    VideoAlreadyExistsError,
)
from tests.conftest import FakeStorageService, FakeUnitOfWork, make_media, make_product

pytestmark = pytest.mark.unit

MEGABYTE = 1024 * 1024


def upload_request(**overrides) -> MediaUploadUrlRequest:
    values: dict = {
        "product_id": 1,
        "merchant_id": 1,
        "media_type": MediaType.IMAGE,
        "content_type": "image/jpeg",
        "file_size": 2 * MEGABYTE,
    }
    values.update(overrides)
    return MediaUploadUrlRequest(**values)


def confirm_request(**overrides) -> ConfirmMediaUploadRequest:
    values: dict = {
        "product_id": 1,
        "merchant_id": 1,
        "media_type": MediaType.IMAGE,
        "storage_key": "products/1/images/abc.jpg",
        "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
        "file_size": 2 * MEGABYTE,
    }
    values.update(overrides)
    return ConfirmMediaUploadRequest(**values)


def reorder_request(**overrides) -> ReorderMediaRequest:
    values: dict = {
        "product_id": 1,
        "merchant_id": 1,
        "items": [ReorderMediaItemDTO(media_id=1, position=0)],
    }
    values.update(overrides)
    return ReorderMediaRequest(**values)


async def test_get_media_upload_url_returns_presigned_url():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    result = await GetMediaUploadUrlUseCase(uow, storage)(upload_request())

    assert result.storage_key.startswith("products/1/images/")
    assert result.storage_key.endswith(".jpg")
    assert result.public_url.endswith(result.storage_key)
    assert storage.presigned == [(result.storage_key, "image/jpeg")]
    assert result.upload_url == f"https://minio.local/presign/{result.storage_key}"


async def test_get_media_upload_url_video_uses_videos_folder():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    result = await GetMediaUploadUrlUseCase(uow, storage)(
        upload_request(
            media_type=MediaType.VIDEO,
            content_type="video/mp4",
            file_size=20 * MEGABYTE,
        )
    )

    assert result.storage_key.startswith("products/1/videos/")
    assert result.storage_key.endswith(".mp4")


async def test_get_media_upload_url_rejects_disallowed_content_type():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    with pytest.raises(MediaValidationError):
        await GetMediaUploadUrlUseCase(uow, storage)(
            upload_request(content_type="image/gif")
        )

    assert storage.presigned == []


async def test_get_media_upload_url_rejects_oversized_image():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    with pytest.raises(MediaValidationError):
        await GetMediaUploadUrlUseCase(uow, storage)(
            upload_request(file_size=10 * MEGABYTE + 1)
        )

    assert storage.presigned == []


async def test_get_media_upload_url_rejects_oversized_video():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    with pytest.raises(MediaValidationError):
        await GetMediaUploadUrlUseCase(uow, storage)(
            upload_request(
                media_type=MediaType.VIDEO,
                content_type="video/mp4",
                file_size=50 * MEGABYTE + 1,
            )
        )


async def test_get_media_upload_url_product_not_found():
    storage = FakeStorageService()
    uow = FakeUnitOfWork()

    with pytest.raises(ProductNotFoundError):
        await GetMediaUploadUrlUseCase(uow, storage)(upload_request())


async def test_get_media_upload_url_wrong_merchant():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=99)])

    with pytest.raises(AccessDeniedError):
        await GetMediaUploadUrlUseCase(uow, storage)(upload_request())

    assert storage.presigned == []


async def test_get_media_upload_url_second_video_rejected():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[make_media(id_=1, product_id=1, media_type="VIDEO")],
    )

    with pytest.raises(VideoAlreadyExistsError):
        await GetMediaUploadUrlUseCase(uow, storage)(
            upload_request(
                media_type=MediaType.VIDEO,
                content_type="video/mp4",
                file_size=20 * MEGABYTE,
            )
        )

    assert storage.presigned == []


async def test_confirm_media_upload_assigns_next_position():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[
            make_media(id_=1, product_id=1, position=0),
            make_media(id_=2, product_id=1, position=1),
        ],
    )

    record = await ConfirmMediaUploadUseCase(uow)(confirm_request())

    assert record.position == 2
    assert record.media_type == MediaType.IMAGE
    assert record.file_size == 2 * MEGABYTE
    assert len(uow.media.records) == 3


async def test_confirm_media_upload_video():
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    record = await ConfirmMediaUploadUseCase(uow)(
        confirm_request(
            media_type=MediaType.VIDEO,
            storage_key="products/1/videos/abc.mp4",
            duration_seconds=30,
        )
    )

    assert record.media_type == MediaType.VIDEO
    assert record.duration_seconds == 30


async def test_confirm_media_upload_rejects_foreign_storage_key():
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    with pytest.raises(MediaValidationError):
        await ConfirmMediaUploadUseCase(uow)(
            confirm_request(storage_key="products/2/images/abc.jpg")
        )

    assert uow.media.records == []


async def test_confirm_media_upload_wrong_merchant():
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=99)])

    with pytest.raises(AccessDeniedError):
        await ConfirmMediaUploadUseCase(uow)(confirm_request())

    assert uow.media.records == []


async def test_confirm_media_upload_second_video_rejected():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[make_media(id_=1, product_id=1, media_type="VIDEO")],
    )

    with pytest.raises(VideoAlreadyExistsError):
        await ConfirmMediaUploadUseCase(uow)(
            confirm_request(
                media_type=MediaType.VIDEO,
                storage_key="products/1/videos/abc.mp4",
            )
        )

    assert len(uow.media.records) == 1


async def test_delete_media_removes_object_and_record():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[
            make_media(id_=5, product_id=1, storage_key="products/1/images/old.jpg")
        ],
    )

    await DeleteMediaUseCase(uow, storage)(
        DeleteMediaRequest(product_id=1, merchant_id=1, media_id=5)
    )

    assert storage.deleted == ["products/1/images/old.jpg"]
    assert uow.media.records == []


async def test_delete_media_unknown_id():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=1)])

    with pytest.raises(MediaNotFoundError):
        await DeleteMediaUseCase(uow, storage)(
            DeleteMediaRequest(product_id=1, merchant_id=1, media_id=42)
        )

    assert storage.deleted == []


async def test_delete_media_wrong_merchant():
    storage = FakeStorageService()
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=99)],
        media=[make_media(id_=5, product_id=1)],
    )

    with pytest.raises(AccessDeniedError):
        await DeleteMediaUseCase(uow, storage)(
            DeleteMediaRequest(product_id=1, merchant_id=1, media_id=5)
        )

    assert storage.deleted == []
    assert len(uow.media.records) == 1


async def test_reorder_media_updates_positions():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[
            make_media(id_=1, product_id=1, position=0),
            make_media(id_=2, product_id=1, position=1),
        ],
    )

    await ReorderMediaUseCase(uow)(
        reorder_request(
            items=[
                ReorderMediaItemDTO(media_id=1, position=1),
                ReorderMediaItemDTO(media_id=2, position=0),
            ]
        )
    )

    positions = {r.id: r.position for r in uow.media.records}
    assert positions == {1: 1, 2: 0}


async def test_reorder_media_rejects_unknown_media():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[make_media(id_=1, product_id=1)],
    )

    with pytest.raises(MediaValidationError):
        await ReorderMediaUseCase(uow)(
            reorder_request(items=[ReorderMediaItemDTO(media_id=42, position=0)])
        )


async def test_reorder_media_rejects_media_of_other_product():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[make_media(id_=1, product_id=2)],
    )

    with pytest.raises(MediaValidationError):
        await ReorderMediaUseCase(uow)(
            reorder_request(items=[ReorderMediaItemDTO(media_id=1, position=0)])
        )


async def test_reorder_media_rejects_duplicate_ids():
    uow = FakeUnitOfWork(
        products=[make_product(id_=1, merchant_id=1)],
        media=[make_media(id_=1, product_id=1), make_media(id_=2, product_id=1)],
    )

    with pytest.raises(MediaValidationError):
        await ReorderMediaUseCase(uow)(
            reorder_request(
                items=[
                    ReorderMediaItemDTO(media_id=1, position=0),
                    ReorderMediaItemDTO(media_id=1, position=1),
                ]
            )
        )


async def test_reorder_media_wrong_merchant():
    uow = FakeUnitOfWork(products=[make_product(id_=1, merchant_id=99)])

    with pytest.raises(AccessDeniedError):
        await ReorderMediaUseCase(uow)(reorder_request())
