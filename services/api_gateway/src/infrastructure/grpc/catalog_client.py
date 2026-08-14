import grpc.aio

from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryResult,
    CategoryUpdateDTO,
    ProductCreateDTO,
    ProductListQuery,
    ProductListResult,
    ProductResult,
    ProductUpdateDTO,
)
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc
from src.infrastructure.grpc.errors import translate_grpc_error


def _to_category_result(response: catalog_pb2.Category) -> CategoryResult:
    return CategoryResult(
        id=response.id,
        name=response.name,
        path=response.path,
        is_active=response.is_active,
        created_at=response.created_at.ToDatetime(),
        updated_at=response.updated_at.ToDatetime(),
    )


def _to_product_result(response: catalog_pb2.Product) -> ProductResult:
    return ProductResult(
        id=response.id,
        category_id=response.category_id,
        title=response.title,
        description=response.description,
        price=response.price,
        stock=response.stock,
        is_active=response.is_active,
        created_at=response.created_at.ToDatetime(),
        updated_at=response.updated_at.ToDatetime(),
    )


class CatalogClient(AbstractCatalogGateway):
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = catalog_pb2_grpc.CatalogServiceStub(channel)

    async def create_category(self, data: CategoryCreateDTO) -> CategoryResult:
        try:
            response = await self._stub.CreateCategory(
                catalog_pb2.CreateCategoryRequest(
                    name=data.name, parent_id=data.parent_id
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_category_result(response)

    async def read_category(self, category_id: int) -> CategoryResult:
        try:
            response = await self._stub.ReadCategory(
                catalog_pb2.CategoryIdRequest(category_id=category_id)
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_category_result(response)

    async def read_list_categories(
        self, query: CategoryListQuery
    ) -> list[CategoryResult]:
        try:
            response = await self._stub.ReadListCategories(
                catalog_pb2.ListCategoriesRequest()
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return [_to_category_result(category) for category in response.categories]

    async def update_category(
        self, category_id: int, data: CategoryUpdateDTO
    ) -> CategoryResult:
        request = catalog_pb2.UpdateCategoryRequest(category_id=category_id)
        if data.name is not None:
            request.name = data.name
        if data.path is not None:
            request.path = data.path
        if data.is_active is not None:
            request.is_active = data.is_active
        try:
            response = await self._stub.UpdateCategory(request)
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_category_result(response)

    async def delete_category(self, category_id: int) -> None:
        try:
            await self._stub.DeleteCategory(
                catalog_pb2.CategoryIdRequest(category_id=category_id)
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc

    async def create_product(self, data: ProductCreateDTO) -> ProductResult:
        try:
            response = await self._stub.CreateProduct(
                catalog_pb2.CreateProductRequest(
                    category_id=data.category_id,
                    title=data.title,
                    description=data.description or None,
                    price=data.price,
                    stock=data.stock,
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_product_result(response)

    async def read_product(self, product_id: int) -> ProductResult:
        try:
            response = await self._stub.ReadProduct(
                catalog_pb2.ProductIdRequest(product_id=product_id)
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_product_result(response)

    async def read_list_products(self, query: ProductListQuery) -> ProductListResult:
        try:
            response = await self._stub.ReadListProducts(
                catalog_pb2.ListProductsRequest(limit=query.limit, offset=query.offset)
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return ProductListResult(
            products=[_to_product_result(product) for product in response.products],
            count=response.count,
        )

    async def update_product(
        self, product_id: int, data: ProductUpdateDTO
    ) -> ProductResult:
        request = catalog_pb2.UpdateProductRequest(product_id=product_id)
        if data.category_id is not None:
            request.category_id = data.category_id
        if data.title is not None:
            request.title = data.title
        if data.description is not None:
            request.description = data.description
        if data.price is not None:
            request.price = data.price
        if data.stock is not None:
            request.stock = data.stock
        if data.is_active is not None:
            request.is_active = data.is_active
        try:
            response = await self._stub.UpdateProduct(request)
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
        return _to_product_result(response)

    async def delete_product(self, product_id: int) -> None:
        try:
            await self._stub.DeleteProduct(
                catalog_pb2.ProductIdRequest(product_id=product_id)
            )
        except grpc.aio.AioRpcError as exc:
            raise translate_grpc_error(exc) from exc
