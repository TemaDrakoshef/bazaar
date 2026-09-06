from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.domain.dtos.catalog import (
    ConfirmMediaUploadInput,
    DeleteMediaInput,
    MediaUploadUrlInput,
    ReorderMediaInput,
)
from src.domain.dtos.seller import VerifyAccessResult
from src.domain.exceptions import ConflictError
from tests.conftest import product_media_result, product_result

pytestmark = pytest.mark.unit

AUTH_HEADER = {"Authorization": "Bearer access-token"}
MERCHANT_HEADER = {**AUTH_HEADER, "X-Merchant-ID": "1"}
UPLOAD_URL_BODY = {
    "media_type": "IMAGE",
    "content_type": "image/jpeg",
    "file_size": 1024,
}


def test_get_media_upload_url_returns_presigned_url(test_client, mock_catalog_gateway):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/upload-url",
        json=UPLOAD_URL_BODY,
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["storage_key"].startswith("products/1/images/")
    assert body["public_url"].endswith(body["storage_key"])
    assert body["upload_url"]
    request = mock_catalog_gateway.get_media_upload_url.await_args.args[0]
    assert isinstance(request, MediaUploadUrlInput)
    assert request.product_id == 1
    assert request.merchant_id == 1


def test_get_media_upload_url_requires_merchant_header(
    test_client, mock_catalog_gateway
):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/upload-url",
        json=UPLOAD_URL_BODY,
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 422


def test_get_media_upload_url_invalid_body_returns_422(
    test_client, mock_catalog_gateway
):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/upload-url",
        json={**UPLOAD_URL_BODY, "file_size": 0},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 422


def test_get_media_upload_url_video_conflict_returns_400(
    test_client, mock_catalog_gateway
):
    mock_catalog_gateway.get_media_upload_url = AsyncMock(
        side_effect=ConflictError("video already exists for this product")
    )

    resp = test_client.post(
        "/api/v1/seller/products/1/media/upload-url",
        json={**UPLOAD_URL_BODY, "media_type": "VIDEO", "content_type": "video/mp4"},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 400
    assert "video" in resp.json()["detail"]


def test_confirm_media_upload_returns_201(test_client, mock_catalog_gateway):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/confirm",
        json={
            "media_type": "IMAGE",
            "storage_key": "products/1/images/abc.jpg",
            "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
            "file_size": 1024,
        },
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 201
    request = mock_catalog_gateway.confirm_media_upload.await_args.args[0]
    assert isinstance(request, ConfirmMediaUploadInput)
    assert request.storage_key == "products/1/images/abc.jpg"


def test_confirm_media_upload_requires_merchant_header(
    test_client, mock_catalog_gateway
):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/confirm",
        json={
            "media_type": "IMAGE",
            "storage_key": "products/1/images/abc.jpg",
            "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
            "file_size": 1024,
        },
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 422


def test_confirm_media_upload_invalid_body_returns_422(
    test_client, mock_catalog_gateway
):
    resp = test_client.post(
        "/api/v1/seller/products/1/media/confirm",
        json={
            "media_type": "IMAGE",
            "storage_key": "products/1/images/abc.jpg",
            "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
            "file_size": 0,
        },
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 422


def test_delete_media_returns_204(test_client, mock_catalog_gateway):
    resp = test_client.delete(
        "/api/v1/seller/products/1/media/5",
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 204
    request = mock_catalog_gateway.delete_media.await_args.args[0]
    assert isinstance(request, DeleteMediaInput)
    assert request.product_id == 1
    assert request.media_id == 5
    assert request.merchant_id == 1


def test_delete_media_requires_merchant_header(test_client, mock_catalog_gateway):
    resp = test_client.delete(
        "/api/v1/seller/products/1/media/5",
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 422


def test_reorder_media_returns_204(test_client, mock_catalog_gateway):
    resp = test_client.patch(
        "/api/v1/seller/products/1/media/reorder",
        json={
            "items": [{"media_id": 1, "position": 1}, {"media_id": 2, "position": 0}]
        },
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 204
    request = mock_catalog_gateway.reorder_media.await_args.args[0]
    assert isinstance(request, ReorderMediaInput)
    assert request.product_id == 1
    assert request.items[0].media_id == 1


def test_reorder_media_empty_items_returns_422(test_client, mock_catalog_gateway):
    resp = test_client.patch(
        "/api/v1/seller/products/1/media/reorder",
        json={"items": []},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 422


def test_reorder_media_requires_merchant_header(test_client, mock_catalog_gateway):
    resp = test_client.patch(
        "/api/v1/seller/products/1/media/reorder",
        json={"items": [{"media_id": 1, "position": 0}]},
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 422


def test_read_own_product_includes_media(test_client, mock_catalog_gateway):
    media = [product_media_result()]
    mock_catalog_gateway.read_product = AsyncMock(
        return_value=product_result(media=media)
    )

    resp = test_client.get(
        "/api/v1/seller/products/1",
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["merchant_id"] == 1
    assert len(body["media"]) == 1
    assert body["media"][0]["url"] == media[0].url


def test_read_own_product_forbidden_for_other_merchant(
    test_client, mock_catalog_gateway
):
    mock_catalog_gateway.read_product = AsyncMock(
        return_value=product_result(merchant_id=99)
    )

    resp = test_client.get(
        "/api/v1/seller/products/1",
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 403
    payload = {
        "media_type": "IMAGE",
        "storage_key": "products/1/images/abc.jpg",
        "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
        "file_size": 1024,
        "width": 900,
        "height": 1200,
    }

    resp = test_client.post(
        "/api/v1/seller/products/1/media/confirm",
        json=payload,
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["media_type"] == "IMAGE"
    assert body["position"] == 0
    request = mock_catalog_gateway.confirm_media_upload.await_args.args[0]
    assert isinstance(request, ConfirmMediaUploadInput)
    assert request.storage_key == "products/1/images/abc.jpg"


def test_confirm_media_upload_not_found_returns_404(test_client, mock_catalog_gateway):
    from src.domain.exceptions import NotFoundError

    mock_catalog_gateway.confirm_media_upload = AsyncMock(
        side_effect=NotFoundError("product not found")
    )

    resp = test_client.post(
        "/api/v1/seller/products/1/media/confirm",
        json={
            "media_type": "IMAGE",
            "storage_key": "products/1/images/abc.jpg",
            "public_url": "http://localhost:9000/bazaar-media/products/1/images/abc.jpg",
            "file_size": 1024,
        },
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 404


def test_delete_media_no_access_returns_403(test_client, mock_seller_gateway):
    mock_seller_gateway.verify_access.return_value = VerifyAccessResult(
        allowed=False, role=""
    )

    resp = test_client.delete(
        "/api/v1/seller/products/1/media/5", headers=MERCHANT_HEADER
    )

    assert resp.status_code == 403


def test_reorder_media_invalid_body_returns_422(test_client, mock_catalog_gateway):
    resp = test_client.patch(
        "/api/v1/seller/products/1/media/reorder",
        json={"items": []},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 422


def test_seller_product_includes_media(test_client, mock_catalog_gateway):
    media = product_media_result()
    mock_catalog_gateway.read_product = AsyncMock(
        return_value=product_result(media=[media])
    )

    resp = test_client.get("/api/v1/seller/products/1", headers=MERCHANT_HEADER)

    assert resp.status_code == 200
    body = resp.json()
    assert body["media"][0]["id"] == 1
    assert body["media"][0]["url"].endswith("products/1/images/img.jpg")
