from __future__ import annotations

from collections.abc import AsyncIterator

import grpc
import pytest
from google.protobuf.empty_pb2 import Empty

from src.application.use_cases.create_category import CreateCategoryUseCase
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_category import DeleteCategoryUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.read_category import ReadCategoryUseCase
from src.application.use_cases.read_list_category import ReadListCategoriesUseCase
from src.application.use_cases.read_list_products import ReadListProductsUseCase
from src.application.use_cases.read_product import ReadProductUseCase
from src.application.use_cases.update_category import UpdateCategoryUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
from src.domain.dtos.category import CategoryCreateDTO, CategoryUpdateDTO
from src.domain.dtos.product import (
    ProductCreateDTO,
    ProductListQueryDTO,
    ProductUpdateDTO,
)
from src.domain.exceptions import ApplicationError
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc
from src.presentation.grpc.handlers import _abort, _to_category, _to_product
from tests.conftest import FakeUnitOfWork, make_category, make_product

pytestmark = pytest.mark.unit


class FakeCatalogServiceHandler(catalog_pb2_grpc.CatalogServiceServicer):
    def __init__(self, uow_factory=None):
        self._uow_factory = uow_factory or (lambda: FakeUnitOfWork())

    @staticmethod
    async def _abort(context, exc: ApplicationError) -> None:
        await _abort(context, exc)

    async def CreateProduct(self, request, context):
        uc = CreateProductUseCase(self._uow_factory())
        try:
            result = await uc(
                ProductCreateDTO(
                    category_id=request.category_id,
                    title=request.title,
                    description=request.description or None,
                    price=request.price,
                    stock=request.stock,
                )
            )
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_product(result)

    async def ReadProduct(self, request, context):
        uc = ReadProductUseCase(self._uow_factory())
        try:
            result = await uc(request.product_id)
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_product(result)

    async def ReadListProducts(self, request, context):
        uc = ReadListProductsUseCase(self._uow_factory())
        try:
            products, count = await uc(
                ProductListQueryDTO(limit=request.limit, offset=request.offset)
            )
        except ApplicationError as exc:
            await self._abort(context, exc)
        return catalog_pb2.ListProductsResponse(
            products=[_to_product(product) for product in products], count=count
        )

    async def UpdateProduct(self, request, context):
        uc = UpdateProductUseCase(self._uow_factory())
        try:
            result = await uc(
                request.product_id,
                ProductUpdateDTO(
                    category_id=request.category_id or None,
                    title=request.title or None,
                    description=request.description or None,
                    price=request.price or None,
                    stock=request.stock or None,
                    is_active=request.is_active or None,
                ),
            )
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_product(result)

    async def DeleteProduct(self, request, context):
        uc = DeleteProductUseCase(self._uow_factory())
        try:
            await uc(request.product_id)
        except ApplicationError as exc:
            await self._abort(context, exc)
        return Empty()

    async def CreateCategory(self, request, context):
        uc = CreateCategoryUseCase(self._uow_factory())
        try:
            result = await uc(
                CategoryCreateDTO(
                    name=request.name,
                    parent_id=request.parent_id,
                )
            )
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_category(result)

    async def ReadCategory(self, request, context):
        uc = ReadCategoryUseCase(self._uow_factory())
        try:
            result = await uc(request.category_id)
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_category(result)

    async def ReadListCategories(self, request, context):
        uc = ReadListCategoriesUseCase(self._uow_factory())
        try:
            result = await uc()
        except ApplicationError as exc:
            await self._abort(context, exc)
        return catalog_pb2.ListCategoriesResponse(
            categories=[_to_category(category) for category in result]
        )

    async def UpdateCategory(self, request, context):
        uc = UpdateCategoryUseCase(self._uow_factory())
        try:
            result = await uc(
                request.category_id,
                CategoryUpdateDTO(
                    name=request.name or None,
                    path=request.path or None,
                    is_active=request.is_active or None,
                ),
            )
        except ApplicationError as exc:
            await self._abort(context, exc)
        return _to_category(result)

    async def DeleteCategory(self, request, context):
        uc = DeleteCategoryUseCase(self._uow_factory())
        try:
            await uc(request.category_id)
        except ApplicationError as exc:
            await self._abort(context, exc)
        return catalog_pb2.Empty()


async def _serve(
    uow_factory,
) -> tuple[catalog_pb2_grpc.CatalogServiceStub, AsyncIterator]:
    server = grpc.aio.server()
    handler = FakeCatalogServiceHandler(uow_factory=uow_factory)
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(handler, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
    stub = catalog_pb2_grpc.CatalogServiceStub(channel)

    async def stop():
        await channel.close()
        await server.stop(0)

    return stub, stop


@pytest.fixture
async def empty_stub() -> AsyncIterator[catalog_pb2_grpc.CatalogServiceStub]:
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    yield stub
    await stop()


async def test_read_product_success_via_grpc():
    product = make_product(id_=1, category_id=1)
    stub, stop = await _serve(lambda: FakeUnitOfWork(products=[product]))
    try:
        resp = await stub.ReadProduct(catalog_pb2.ProductIdRequest(product_id=1))
        assert resp.id == 1
        assert resp.title == "product"
    finally:
        await stop()


async def test_read_product_nonexistent_aborts_not_found(empty_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await empty_stub.ReadProduct(catalog_pb2.ProductIdRequest(product_id=999))
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert exc_info.value.details() == "product not found"


async def test_update_product_success_via_grpc():
    product = make_product(id_=1, category_id=1)
    category = make_category(id_=1)
    stub, stop = await _serve(
        lambda: FakeUnitOfWork(products=[product], categories=[category])
    )
    try:
        resp = await stub.UpdateProduct(
            catalog_pb2.UpdateProductRequest(product_id=1, title="updated", price=200)
        )
        assert resp.id == 1
        assert resp.title == "updated"
    finally:
        await stop()


async def test_update_product_nonexistent_aborts_not_found(empty_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await empty_stub.UpdateProduct(
            catalog_pb2.UpdateProductRequest(product_id=999, title="updated")
        )
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert exc_info.value.details() == "999"


async def test_delete_product_success_via_grpc():
    product = make_product(id_=1, category_id=1)
    stub, stop = await _serve(lambda: FakeUnitOfWork(products=[product]))
    try:
        resp = await stub.DeleteProduct(catalog_pb2.ProductIdRequest(product_id=1))
        assert resp is not None
    finally:
        await stop()


async def test_delete_product_nonexistent_aborts_not_found(empty_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await empty_stub.DeleteProduct(catalog_pb2.ProductIdRequest(product_id=999))
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert exc_info.value.details() == "999"
