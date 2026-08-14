from datetime import datetime

from dishka.integrations.grpcio import FromDishka, inject
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext

from src.application.use_cases.create_category import (
    CreateCategoryUseCase,
)
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_category import DeleteCategoryUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.read_category import (
    ReadCategoryUseCase,
)
from src.application.use_cases.read_list_category import (
    ReadListCategoriesUseCase,
)
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
from src.domain.entities.category import Category
from src.domain.entities.product import Product
from src.domain.exceptions import ApplicationError
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc


def _to_timestamp(value: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(value)
    return timestamp


def _to_category(category: Category) -> catalog_pb2.Category:
    return catalog_pb2.Category(
        id=category.id,
        name=category.name,
        path=category.path,
        is_active=category.is_active,
        created_at=_to_timestamp(category.created_at),
        updated_at=_to_timestamp(category.updated_at),
    )


def _to_product(product: Product) -> catalog_pb2.Product:
    return catalog_pb2.Product(
        id=product.id,
        category_id=product.category_id,
        title=product.title,
        description=product.description,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
        created_at=_to_timestamp(product.created_at),
        updated_at=_to_timestamp(product.updated_at),
    )


class CatalogServiceHandler(catalog_pb2_grpc.CatalogServiceServicer):
    @inject
    async def CreateProduct(
        self,
        request: catalog_pb2.CreateProductRequest,
        context: ServicerContext,
        create_product: FromDishka[CreateProductUseCase],
    ) -> catalog_pb2.Product:
        try:
            result = await create_product(
                ProductCreateDTO(
                    category_id=request.category_id,
                    title=request.title,
                    description=request.description or None,
                    price=request.price,
                    stock=request.stock,
                )
            )
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return _to_product(result)

    @inject
    async def ReadProduct(
        self,
        request: catalog_pb2.ProductIdRequest,
        context: ServicerContext,
        read_product: FromDishka[ReadProductUseCase],
    ) -> catalog_pb2.Product:
        try:
            result = await read_product(request.product_id)
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return _to_product(result)

    @inject
    async def ReadListProducts(
        self,
        request: catalog_pb2.ListProductsRequest,
        context: ServicerContext,
        read_list_products: FromDishka[ReadListProductsUseCase],
    ) -> catalog_pb2.ListProductsResponse:
        try:
            products, count = await read_list_products(
                ProductListQueryDTO(limit=request.limit, offset=request.offset)
            )
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return catalog_pb2.ListProductsResponse(
            products=[_to_product(product) for product in products], count=count
        )

    @inject
    async def UpdateProduct(
        self,
        request: catalog_pb2.UpdateProductRequest,
        context: ServicerContext,
        update_product: FromDishka[UpdateProductUseCase],
    ) -> catalog_pb2.Product:
        try:
            result = await update_product(
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
            await context.abort(exc.grpc_code, exc.detail)

        return _to_product(result)

    @inject
    async def DeleteProduct(
        self,
        request: catalog_pb2.ProductIdRequest,
        context: ServicerContext,
        delete_product: FromDishka[DeleteProductUseCase],
    ) -> Empty:
        try:
            await delete_product(request.product_id)
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return Empty()

    @inject
    async def CreateCategory(
        self,
        request: catalog_pb2.CreateCategoryRequest,
        context: ServicerContext,
        create_category: FromDishka["CreateCategoryUseCase"],
    ) -> catalog_pb2.Category:
        try:
            result = await create_category(
                CategoryCreateDTO(
                    name=request.name,
                    parent_id=request.parent_id,
                )
            )
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return _to_category(result)

    @inject
    async def ReadCategory(
        self,
        request: catalog_pb2.CategoryIdRequest,
        context: ServicerContext,
        read_category: FromDishka["ReadCategoryUseCase"],
    ) -> catalog_pb2.Category:
        try:
            result = await read_category(request.category_id)
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return _to_category(result)

    @inject
    async def ReadListCategories(
        self,
        request: catalog_pb2.ListCategoriesRequest,
        context: ServicerContext,
        read_list_categories: FromDishka["ReadListCategoriesUseCase"],
    ) -> catalog_pb2.ListCategoriesResponse:
        try:
            result = await read_list_categories()
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return catalog_pb2.ListCategoriesResponse(
            categories=[_to_category(category) for category in result]
        )

    @inject
    async def UpdateCategory(
        self,
        request: catalog_pb2.UpdateCategoryRequest,
        context: ServicerContext,
        update_category: FromDishka["UpdateCategoryUseCase"],
    ) -> catalog_pb2.Category:
        try:
            result = await update_category(
                request.category_id,
                CategoryUpdateDTO(
                    name=request.name or None,
                    path=request.path or None,
                    is_active=request.is_active or None,
                ),
            )
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return _to_category(result)

    @inject
    async def DeleteCategory(
        self,
        request: catalog_pb2.CategoryIdRequest,
        context: ServicerContext,
        delete_category: FromDishka["DeleteCategoryUseCase"],
    ) -> Empty:
        try:
            await delete_category(request.category_id)
        except ApplicationError as exc:
            await context.abort(exc.grpc_code, exc.detail)

        return Empty()
