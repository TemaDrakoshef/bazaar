from __future__ import annotations

import pytest

from src.domain.dtos.catalog import (
    CategoryResult,
    ProductListResult,
    ProductResult,
)
from src.domain.exceptions import NotFoundError
from tests.conftest import category_result, product_result

pytestmark = pytest.mark.unit


def _category() -> CategoryResult:
    return category_result()


def _product() -> ProductResult:
    return product_result()


def test_create_category_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.create_category.return_value = _category()

    resp = test_client.post("/api/v1/catalog/category", json={"name": "clothes"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["name"] == "category"
    assert body["path"] == "1"


def test_create_category_missing_parent_id_maps_to_404(
    test_client, mock_catalog_gateway
):
    mock_catalog_gateway.create_category.side_effect = NotFoundError(
        "category not found"
    )

    resp = test_client.post(
        "/api/v1/catalog/category", json={"name": "clothes", "parent_id": 999}
    )

    assert resp.status_code == 404


def test_read_category_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.read_category.return_value = _category()

    resp = test_client.get("/api/v1/catalog/category/1")

    assert resp.status_code == 200
    assert resp.json()["id"] == 1
    mock_catalog_gateway.read_category.assert_awaited_once_with(1)


def test_read_list_categories_returns_list(test_client, mock_catalog_gateway):
    mock_catalog_gateway.read_list_categories.return_value = [_category()]

    resp = test_client.get("/api/v1/catalog/category")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["name"] == "category"


def test_update_category_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.update_category.return_value = _category()

    resp = test_client.patch("/api/v1/catalog/category/1", json={"name": "new"})

    assert resp.status_code == 200
    assert resp.json()["name"] == "category"
    mock_catalog_gateway.update_category.assert_awaited_once()


def test_delete_category_returns_204(test_client, mock_catalog_gateway):
    mock_catalog_gateway.delete_category.return_value = None

    resp = test_client.delete("/api/v1/catalog/category/1")

    assert resp.status_code == 204
    mock_catalog_gateway.delete_category.assert_awaited_once_with(1)


def test_create_product_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.create_product.return_value = _product()

    resp = test_client.post(
        "/api/v1/catalog/product",
        json={"category_id": 1, "title": "product", "price": 100, "stock": 5},
    )

    assert resp.status_code == 201
    assert resp.json()["id"] == 1
    assert resp.json()["title"] == "product"


def test_read_product_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.read_product.return_value = _product()

    resp = test_client.get("/api/v1/catalog/product/1")

    assert resp.status_code == 200
    assert resp.json()["category_id"] == 1
    mock_catalog_gateway.read_product.assert_awaited_once_with(1)


def test_read_list_products_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.read_list_products.return_value = ProductListResult(
        products=[_product()], count=1
    )

    resp = test_client.get("/api/v1/catalog/product")

    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    assert resp.json()["products"][0]["title"] == "product"


def test_update_product_returns_mapped_response(test_client, mock_catalog_gateway):
    mock_catalog_gateway.update_product.return_value = _product()

    resp = test_client.patch(
        "/api/v1/catalog/product/1", json={"title": "updated", "price": 200}
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "product"
    mock_catalog_gateway.update_product.assert_awaited_once()


def test_delete_product_returns_204(test_client, mock_catalog_gateway):
    mock_catalog_gateway.delete_product.return_value = None

    resp = test_client.delete("/api/v1/catalog/product/1")

    assert resp.status_code == 204
    mock_catalog_gateway.delete_product.assert_awaited_once_with(1)


def test_read_product_missing_maps_to_404(test_client, mock_catalog_gateway):
    mock_catalog_gateway.read_product.side_effect = NotFoundError("product not found")

    resp = test_client.get("/api/v1/catalog/product/999")

    assert resp.status_code == 404


def test_update_product_missing_maps_to_404(test_client, mock_catalog_gateway):
    mock_catalog_gateway.update_product.side_effect = NotFoundError("product not found")

    resp = test_client.patch("/api/v1/catalog/product/999", json={"title": "updated"})

    assert resp.status_code == 404


def test_delete_product_missing_maps_to_404(test_client, mock_catalog_gateway):
    mock_catalog_gateway.delete_product.side_effect = NotFoundError("product not found")

    resp = test_client.delete("/api/v1/catalog/product/999")

    assert resp.status_code == 404
