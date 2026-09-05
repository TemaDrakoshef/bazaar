from __future__ import annotations

import pytest

from src.domain.dtos.seller import VerifyAccessResult

pytestmark = pytest.mark.unit

AUTH_HEADER = {"Authorization": "Bearer access-token"}
MERCHANT_HEADER = {**AUTH_HEADER, "X-Merchant-ID": "1"}


def test_create_merchant_returns_201(test_client, mock_seller_gateway):
    resp = test_client.post(
        "/api/v1/merchants",
        json={"name": "shop", "inn": "7707083893"},
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["owner_user_id"] == "user-123"
    assert body["status"] == "ACTIVE"


def test_create_merchant_requires_auth(test_client, mock_seller_gateway):
    resp = test_client.post(
        "/api/v1/merchants", json={"name": "shop", "inn": "7707083893"}
    )

    assert resp.status_code == 401


def test_create_merchant_invalid_inn_returns_422(test_client, mock_seller_gateway):
    resp = test_client.post(
        "/api/v1/merchants",
        json={"name": "shop", "inn": "123"},
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 422


def test_list_my_merchants_returns_list(test_client, mock_seller_gateway):
    resp = test_client.get("/api/v1/merchants/my", headers=AUTH_HEADER)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["name"] == "shop"
    mock_seller_gateway.list_user_merchants.assert_awaited_once_with("user-123")


def test_seller_create_product_returns_201(test_client, mock_catalog_gateway):
    resp = test_client.post(
        "/api/v1/seller/products",
        json={"category_id": 1, "title": "product", "price": 100, "stock": 5},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 201
    assert resp.json()["merchant_id"] == 1


def test_seller_list_products_filters_by_merchant(test_client, mock_catalog_gateway):
    resp = test_client.get("/api/v1/seller/products", headers=MERCHANT_HEADER)

    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    query = mock_catalog_gateway.read_list_products.await_args.args[0]
    assert query.merchant_id == 1


def test_seller_update_product_returns_200(test_client, mock_catalog_gateway):
    resp = test_client.patch(
        "/api/v1/seller/products/1",
        json={"title": "updated"},
        headers=MERCHANT_HEADER,
    )

    assert resp.status_code == 200
    merchant_id, product_id, _ = mock_catalog_gateway.update_product.await_args.args
    assert (merchant_id, product_id) == (1, 1)


def test_seller_delete_product_returns_204(test_client, mock_catalog_gateway):
    resp = test_client.delete("/api/v1/seller/products/1", headers=MERCHANT_HEADER)

    assert resp.status_code == 204
    mock_catalog_gateway.delete_product.assert_awaited_once_with(1, 1)


def test_seller_products_without_merchant_header_returns_422(test_client):
    resp = test_client.get("/api/v1/seller/products", headers=AUTH_HEADER)

    assert resp.status_code == 422


def test_seller_products_no_access_returns_403(test_client, mock_seller_gateway):
    mock_seller_gateway.verify_access.return_value = VerifyAccessResult(
        allowed=False, role=""
    )

    resp = test_client.get("/api/v1/seller/products", headers=MERCHANT_HEADER)

    assert resp.status_code == 403
