"""Unit tests for the application layer (use cases).

Each use case is exercised against a mocked gateway port, verifying the DTO is
forwarded untouched and gateway errors propagate unchanged.
"""

from __future__ import annotations

import pytest

from src.application.use_cases.auth.login import LoginUseCase
from src.application.use_cases.auth.logout import LogoutUseCase
from src.application.use_cases.auth.refresh import RefreshUseCase
from src.application.use_cases.auth.signup import SignUpUseCase
from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.application.use_cases.catalog.confirm_media_upload import (
    ConfirmMediaUploadUseCase,
)
from src.application.use_cases.catalog.create_category import CreateCategoryUseCase
from src.application.use_cases.catalog.create_product import CreateProductUseCase
from src.application.use_cases.catalog.delete_category import DeleteCategoryUseCase
from src.application.use_cases.catalog.delete_media import DeleteMediaUseCase
from src.application.use_cases.catalog.delete_product import DeleteProductUseCase
from src.application.use_cases.catalog.get_media_upload_url import (
    GetMediaUploadUrlUseCase,
)
from src.application.use_cases.catalog.read_category import ReadCategoryUseCase
from src.application.use_cases.catalog.read_list_categories import (
    ReadListCategoriesUseCase,
)
from src.application.use_cases.catalog.read_list_products import (
    ReadListProductsUseCase,
)
from src.application.use_cases.catalog.read_product import ReadProductUseCase
from src.application.use_cases.catalog.reorder_media import ReorderMediaUseCase
from src.application.use_cases.catalog.update_category import UpdateCategoryUseCase
from src.application.use_cases.catalog.update_product import UpdateProductUseCase
from src.application.use_cases.seller.create_merchant import CreateMerchantUseCase
from src.application.use_cases.seller.list_merchants import ListUserMerchantsUseCase
from src.application.use_cases.seller.verify_access import VerifyAccessUseCase
from src.domain.dtos.auth import (
    LoginInput,
    LogoutInput,
    RefreshInput,
    SignUpInput,
    ValidateTokenInput,
)
from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryUpdateDTO,
    ConfirmMediaUploadInput,
    DeleteMediaInput,
    MediaUploadUrlInput,
    ProductCreateDTO,
    ProductListQuery,
    ProductMediaResult,
    ProductUpdateDTO,
    ReorderMediaInput,
)
from src.domain.dtos.seller import MerchantCreateInput, VerifyAccessInput
from src.domain.exceptions import UnavailableError

pytestmark = pytest.mark.unit

SIGNUP_INPUT = SignUpInput(
    email="user@example.com", phone="+79990000000", password="S3cr3t-pass!"
)
LOGIN_INPUT = LoginInput(email="user@example.com", password="S3cr3t-pass!")
LOGOUT_INPUT = LogoutInput(session_id="session-1")
REFRESH_INPUT = RefreshInput(refresh_token="refresh-token")
VALIDATE_INPUT = ValidateTokenInput(access_token="access-token")
CATEGORY_INPUT = CategoryCreateDTO(name="clothes", parent_id=None)


async def test_signup_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await SignUpUseCase(mock_auth_gateway).execute(SIGNUP_INPUT)

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    mock_auth_gateway.sign_up.assert_awaited_once_with(SIGNUP_INPUT)


async def test_login_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await LoginUseCase(mock_auth_gateway).execute(LOGIN_INPUT)

    assert result.access_token == "access-token"
    mock_auth_gateway.login.assert_awaited_once_with(LOGIN_INPUT)


async def test_logout_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await LogoutUseCase(mock_auth_gateway).execute(LOGOUT_INPUT)

    assert result is None
    mock_auth_gateway.logout.assert_awaited_once_with(LOGOUT_INPUT)


async def test_refresh_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await RefreshUseCase(mock_auth_gateway).execute(REFRESH_INPUT)

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    mock_auth_gateway.refresh.assert_awaited_once_with(REFRESH_INPUT)


async def test_validate_token_use_case_delegates_to_gateway(mock_auth_gateway):
    result = await ValidateTokenUseCase(mock_auth_gateway).execute(VALIDATE_INPUT)

    assert result.valid is True
    assert result.user_id == "user-123"
    mock_auth_gateway.validate_token.assert_awaited_once_with(VALIDATE_INPUT)


async def test_create_category_use_case_delegates_to_catalog_gateway(
    mock_catalog_gateway,
):
    result = await CreateCategoryUseCase(mock_catalog_gateway).execute(CATEGORY_INPUT)

    assert result.id == 1
    assert result.name == "category"
    mock_catalog_gateway.create_category.assert_awaited_once_with(CATEGORY_INPUT)


async def test_signup_use_case_propagates_gateway_error(mock_auth_gateway):
    mock_auth_gateway.sign_up.side_effect = UnavailableError("auth service down")
    use_case = SignUpUseCase(mock_auth_gateway)

    with pytest.raises(UnavailableError) as exc_info:
        await use_case.execute(SIGNUP_INPUT)
    assert exc_info.value.http_code == 503


async def test_login_use_case_propagates_gateway_error(mock_auth_gateway):
    mock_auth_gateway.login.side_effect = UnavailableError("auth service down")
    use_case = LoginUseCase(mock_auth_gateway)

    with pytest.raises(UnavailableError):
        await use_case.execute(LOGIN_INPUT)


async def test_read_category_use_case_delegates_to_gateway(mock_catalog_gateway):
    result = await ReadCategoryUseCase(mock_catalog_gateway).execute(1)

    assert result.id == 1
    mock_catalog_gateway.read_category.assert_awaited_once_with(1)


async def test_read_list_categories_use_case_delegates_to_gateway(
    mock_catalog_gateway,
):
    query = CategoryListQuery(limit=10, offset=0)
    result = await ReadListCategoriesUseCase(mock_catalog_gateway).execute(query)

    assert result[0].name == "category"
    mock_catalog_gateway.read_list_categories.assert_awaited_once_with(query)


async def test_update_category_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = CategoryUpdateDTO(name="new")
    result = await UpdateCategoryUseCase(mock_catalog_gateway).execute(1, data)

    assert result.id == 1
    mock_catalog_gateway.update_category.assert_awaited_once_with(1, data)


async def test_delete_category_use_case_delegates_to_gateway(mock_catalog_gateway):
    result = await DeleteCategoryUseCase(mock_catalog_gateway).execute(1)

    assert result is None
    mock_catalog_gateway.delete_category.assert_awaited_once_with(1)


async def test_create_product_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = ProductCreateDTO(
        merchant_id=1, category_id=1, title="product", price=100, stock=5
    )
    result = await CreateProductUseCase(mock_catalog_gateway).execute(data)

    assert result.id == 1
    mock_catalog_gateway.create_product.assert_awaited_once_with(data)


async def test_read_product_use_case_delegates_to_gateway(mock_catalog_gateway):
    result = await ReadProductUseCase(mock_catalog_gateway).execute(1)

    assert result.id == 1
    mock_catalog_gateway.read_product.assert_awaited_once_with(1)


async def test_read_list_products_use_case_delegates_to_gateway(
    mock_catalog_gateway,
):
    query = ProductListQuery(limit=10, offset=0)
    result = await ReadListProductsUseCase(mock_catalog_gateway).execute(query)

    assert result.count == 1
    mock_catalog_gateway.read_list_products.assert_awaited_once_with(query)


async def test_update_product_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = ProductUpdateDTO(title="updated")
    result = await UpdateProductUseCase(mock_catalog_gateway).execute(1, 1, data)

    assert result.id == 1
    mock_catalog_gateway.update_product.assert_awaited_once_with(1, 1, data)


async def test_delete_product_use_case_delegates_to_gateway(mock_catalog_gateway):
    result = await DeleteProductUseCase(mock_catalog_gateway).execute(1, 1)

    assert result is None
    mock_catalog_gateway.delete_product.assert_awaited_once_with(1, 1)


async def test_create_merchant_use_case_delegates_to_seller_gateway(
    mock_seller_gateway,
):
    data = MerchantCreateInput(name="shop", inn="7707083893", user_id="user-123")
    result = await CreateMerchantUseCase(mock_seller_gateway).execute(data)

    assert result.id == 1
    assert result.status == "ACTIVE"
    mock_seller_gateway.create_merchant.assert_awaited_once_with(data)


async def test_list_merchants_use_case_delegates_to_seller_gateway(
    mock_seller_gateway,
):
    result = await ListUserMerchantsUseCase(mock_seller_gateway).execute("user-123")

    assert result[0].name == "shop"
    mock_seller_gateway.list_user_merchants.assert_awaited_once_with("user-123")


async def test_verify_access_use_case_delegates_to_seller_gateway(
    mock_seller_gateway,
):
    data = VerifyAccessInput(user_id="user-123", merchant_id=1)
    result = await VerifyAccessUseCase(mock_seller_gateway).execute(data)

    assert result.allowed is True
    assert result.role == "OWNER"
    mock_seller_gateway.verify_access.assert_awaited_once_with(data)


async def test_get_media_upload_url_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = MediaUploadUrlInput(
        product_id=1,
        merchant_id=1,
        media_type="IMAGE",
        content_type="image/jpeg",
        file_size=1024,
    )
    result = await GetMediaUploadUrlUseCase(mock_catalog_gateway).execute(data)

    assert result.upload_url
    mock_catalog_gateway.get_media_upload_url.assert_awaited_once_with(data)


async def test_confirm_media_upload_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = ConfirmMediaUploadInput(
        product_id=1,
        merchant_id=1,
        media_type="IMAGE",
        storage_key="products/1/images/abc.jpg",
        public_url="http://localhost:9000/p.jpg",
        file_size=1024,
    )
    result = await ConfirmMediaUploadUseCase(mock_catalog_gateway).execute(data)

    assert isinstance(result, ProductMediaResult)
    mock_catalog_gateway.confirm_media_upload.assert_awaited_once_with(data)


async def test_delete_media_use_case_delegates_to_gateway(mock_catalog_gateway):
    data = DeleteMediaInput(product_id=1, merchant_id=1, media_id=5)
    result = await DeleteMediaUseCase(mock_catalog_gateway).execute(data)

    assert result is None
    mock_catalog_gateway.delete_media.assert_awaited_once_with(data)


async def test_reorder_media_use_case_delegates_to_gateway(mock_catalog_gateway):
    from src.domain.dtos.catalog import ReorderMediaItemInput

    data = ReorderMediaInput(
        product_id=1,
        merchant_id=1,
        items=[ReorderMediaItemInput(media_id=1, position=0)],
    )
    result = await ReorderMediaUseCase(mock_catalog_gateway).execute(data)

    assert result is None
    mock_catalog_gateway.reorder_media.assert_awaited_once_with(data)
