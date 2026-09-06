from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

import structlog
from dishka.integrations.grpcio import FromDishka, inject
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext
from pydantic import ValidationError as PydanticValidationError
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.application.use_cases.confirm_media_upload import (
    ConfirmMediaUploadUseCase,
)
from src.application.use_cases.create_category import (
    CreateCategoryUseCase,
)
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_category import DeleteCategoryUseCase
from src.application.use_cases.delete_media import DeleteMediaUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.get_media_upload_url import (
    GetMediaUploadUrlUseCase,
)
from src.application.use_cases.move_category import MoveCategoryUseCase
from src.application.use_cases.read_category import (
    ReadCategoryUseCase,
)
from src.application.use_cases.read_list_category import (
    ReadListCategoriesUseCase,
)
from src.application.use_cases.read_list_products import ReadListProductsUseCase
from src.application.use_cases.read_product import ReadProductUseCase
from src.application.use_cases.reorder_media import ReorderMediaUseCase
from src.application.use_cases.update_category import UpdateCategoryUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
from src.domain.dtos.category import (
    CategoryCreateDTO,
    CategoryMoveDTO,
    CategoryUpdateDTO,
)
from src.domain.dtos.media import (
    ConfirmMediaUploadRequest,
    DeleteMediaRequest,
    MediaUploadUrlRequest,
    ReorderMediaItemDTO,
    ReorderMediaRequest,
)
from src.domain.dtos.product import (
    ProductCreateDTO,
    ProductListQueryDTO,
    ProductUpdateDTO,
)
from src.domain.entities.category import Category
from src.domain.entities.media import MediaType, ProductMedia
from src.domain.entities.product import Product
from src.domain.exceptions import ApplicationError, ValidationError
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc

logger = structlog.get_logger()


def _to_timestamp(value: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(value)
    return timestamp


def _to_category(category: Category) -> catalog_pb2.Category:
    result = catalog_pb2.Category(
        id=category.id,
        name=category.name,
        path=category.path,
        is_active=category.is_active,
        created_at=_to_timestamp(category.created_at),
        updated_at=_to_timestamp(category.updated_at),
    )
    if category.parent_id is not None:
        result.parent_id = category.parent_id
    return result


def _to_product(product: Product) -> catalog_pb2.Product:
    result = catalog_pb2.Product(
        id=product.id,
        merchant_id=product.merchant_id,
        category_id=product.category_id,
        title=product.title,
        description=product.description,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
        created_at=_to_timestamp(product.created_at),
        updated_at=_to_timestamp(product.updated_at),
    )
    result.media.extend(_to_product_media(media) for media in product.media)
    return result


def _to_media_type(media_type: MediaType) -> int:
    if media_type == MediaType.IMAGE:
        return int(catalog_pb2.MEDIA_TYPE_IMAGE)
    return int(catalog_pb2.MEDIA_TYPE_VIDEO)


def _from_media_type(value: int) -> MediaType:
    if value == catalog_pb2.MEDIA_TYPE_IMAGE:
        return MediaType.IMAGE
    if value == catalog_pb2.MEDIA_TYPE_VIDEO:
        return MediaType.VIDEO
    raise ValidationError("invalid media type")


def _to_product_media(media: ProductMedia) -> catalog_pb2.ProductMedia:
    result = catalog_pb2.ProductMedia(
        id=media.id,
        product_id=media.product_id,
        media_type=_to_media_type(media.media_type),
        url=media.url,
        position=media.position,
        file_size=media.file_size,
    )
    if media.width is not None:
        result.width = media.width
    if media.height is not None:
        result.height = media.height
    if media.duration_seconds is not None:
        result.duration_seconds = media.duration_seconds
    return result


@contextmanager
def _request_context(**context: object) -> Iterator[None]:
    """Bind structured logging context for the duration of one RPC."""
    bind_contextvars(**context)
    try:
        yield
    finally:
        clear_contextvars()


async def _abort(context: ServicerContext, exc: Exception) -> None:
    """Log a failure and abort the RPC with the matching gRPC status."""
    if isinstance(exc, PydanticValidationError):
        error = ValidationError(str(exc.errors()[0].get("msg", "invalid input")))
    elif isinstance(exc, ApplicationError):
        error = exc
    else:
        logger.exception(
            "catalog.unhandled_error",
            error_type=type(exc).__name__,
            error=repr(exc),
        )
        error = ApplicationError()
    logger.warning(
        "catalog.request_failed",
        error_type=type(error).__name__,
        grpc_code=error.grpc_code.name,
        detail=error.detail,
    )
    await context.abort(error.grpc_code, error.detail)


class CatalogServiceHandler(catalog_pb2_grpc.CatalogServiceServicer):
    @inject
    async def CreateProduct(
        self,
        request: catalog_pb2.CreateProductRequest,
        context: ServicerContext,
        create_product: FromDishka[CreateProductUseCase],
    ) -> catalog_pb2.Product:
        with _request_context(category_id=request.category_id):
            try:
                description = (
                    request.description if request.HasField("description") else None
                )
                result = await create_product(
                    ProductCreateDTO(
                        merchant_id=request.merchant_id,
                        category_id=request.category_id,
                        title=request.title,
                        description=description,
                        price=request.price,
                        stock=request.stock,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return _to_product(result)

    @inject
    async def ReadProduct(
        self,
        request: catalog_pb2.ProductIdRequest,
        context: ServicerContext,
        read_product: FromDishka[ReadProductUseCase],
    ) -> catalog_pb2.Product:
        with _request_context(product_id=request.product_id):
            try:
                result = await read_product(request.product_id)
            except ApplicationError as exc:
                await _abort(context, exc)

            return _to_product(result)

    @inject
    async def ReadListProducts(
        self,
        request: catalog_pb2.ListProductsRequest,
        context: ServicerContext,
        read_list_products: FromDishka[ReadListProductsUseCase],
    ) -> catalog_pb2.ListProductsResponse:
        with _request_context(limit=request.limit, offset=request.offset):
            try:
                merchant_id = (
                    request.merchant_id if request.HasField("merchant_id") else None
                )
                products, count = await read_list_products(
                    ProductListQueryDTO(
                        limit=request.limit,
                        offset=request.offset,
                        merchant_id=merchant_id,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

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
        with _request_context(product_id=request.product_id):
            try:
                category_id = (
                    request.category_id if request.HasField("category_id") else None
                )
                title = request.title if request.HasField("title") else None
                description = (
                    request.description if request.HasField("description") else None
                )
                price = request.price if request.HasField("price") else None
                stock = request.stock if request.HasField("stock") else None
                is_active = request.is_active if request.HasField("is_active") else None
                result = await update_product(
                    request.merchant_id,
                    request.product_id,
                    ProductUpdateDTO(
                        category_id=category_id,
                        title=title,
                        description=description,
                        price=price,
                        stock=stock,
                        is_active=is_active,
                    ),
                )
            except Exception as exc:
                await _abort(context, exc)

            return _to_product(result)

    @inject
    async def DeleteProduct(
        self,
        request: catalog_pb2.DeleteProductRequest,
        context: ServicerContext,
        delete_product: FromDishka[DeleteProductUseCase],
    ) -> Empty:
        with _request_context(product_id=request.product_id):
            try:
                await delete_product(request.merchant_id, request.product_id)
            except Exception as exc:
                await _abort(context, exc)

            return Empty()

    @inject
    async def CreateCategory(
        self,
        request: catalog_pb2.CreateCategoryRequest,
        context: ServicerContext,
        create_category: FromDishka[CreateCategoryUseCase],
    ) -> catalog_pb2.Category:
        with _request_context(parent_id=request.parent_id):
            try:
                parent_id = request.parent_id if request.HasField("parent_id") else None
                result = await create_category(
                    CategoryCreateDTO(name=request.name, parent_id=parent_id),
                )
            except ApplicationError as exc:
                await _abort(context, exc)

            return _to_category(result)

    @inject
    async def ReadCategory(
        self,
        request: catalog_pb2.CategoryIdRequest,
        context: ServicerContext,
        read_category: FromDishka[ReadCategoryUseCase],
    ) -> catalog_pb2.Category:
        with _request_context(category_id=request.category_id):
            try:
                result = await read_category(request.category_id)
            except ApplicationError as exc:
                await _abort(context, exc)

            return _to_category(result)

    @inject
    async def ReadListCategories(
        self,
        request: catalog_pb2.ListCategoriesRequest,
        context: ServicerContext,
        read_list_categories: FromDishka[ReadListCategoriesUseCase],
    ) -> catalog_pb2.ListCategoriesResponse:
        try:
            result = await read_list_categories()
        except ApplicationError as exc:
            await _abort(context, exc)

        return catalog_pb2.ListCategoriesResponse(
            categories=[_to_category(category) for category in result]
        )

    @inject
    async def UpdateCategory(
        self,
        request: catalog_pb2.UpdateCategoryRequest,
        context: ServicerContext,
        update_category: FromDishka[UpdateCategoryUseCase],
    ) -> catalog_pb2.Category:
        with _request_context(category_id=request.category_id):
            try:
                name = request.name if request.HasField("name") else None
                is_active = request.is_active if request.HasField("is_active") else None
                result = await update_category(
                    request.category_id,
                    CategoryUpdateDTO(name=name, is_active=is_active),
                )
            except ApplicationError as exc:
                await _abort(context, exc)

            return _to_category(result)

    @inject
    async def DeleteCategory(
        self,
        request: catalog_pb2.CategoryIdRequest,
        context: ServicerContext,
        delete_category: FromDishka[DeleteCategoryUseCase],
    ) -> Empty:
        with _request_context(category_id=request.category_id):
            try:
                await delete_category(request.category_id)
            except ApplicationError as exc:
                await _abort(context, exc)

            return Empty()

    @inject
    async def MoveCategory(
        self,
        request: catalog_pb2.MoveCategoryRequest,
        context: ServicerContext,
        move_category: FromDishka[MoveCategoryUseCase],
    ) -> catalog_pb2.Category:
        with _request_context(
            category_id=request.category_id, parent_id=request.parent_id
        ):
            try:
                parent_id = request.parent_id if request.HasField("parent_id") else None
                result = await move_category(
                    request.category_id,
                    CategoryMoveDTO(parent_id=parent_id),
                )
            except ApplicationError as exc:
                await _abort(context, exc)

            return _to_category(result)

    @inject
    async def GetMediaUploadUrl(
        self,
        request: catalog_pb2.GetMediaUploadUrlRequest,
        context: ServicerContext,
        get_media_upload_url: FromDishka[GetMediaUploadUrlUseCase],
    ) -> catalog_pb2.GetMediaUploadUrlResponse:
        with _request_context(product_id=request.product_id):
            try:
                result = await get_media_upload_url(
                    MediaUploadUrlRequest(
                        product_id=request.product_id,
                        merchant_id=request.merchant_id,
                        media_type=_from_media_type(request.media_type),
                        content_type=request.content_type,
                        file_size=request.file_size,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return catalog_pb2.GetMediaUploadUrlResponse(
                upload_url=result.upload_url,
                storage_key=result.storage_key,
                public_url=result.public_url,
            )

    @inject
    async def ConfirmMediaUpload(
        self,
        request: catalog_pb2.ConfirmMediaUploadRequest,
        context: ServicerContext,
        confirm_media_upload: FromDishka[ConfirmMediaUploadUseCase],
    ) -> catalog_pb2.ProductMedia:
        with _request_context(product_id=request.product_id):
            try:
                width = request.width if request.HasField("width") else None
                height = request.height if request.HasField("height") else None
                duration = (
                    request.duration_seconds
                    if request.HasField("duration_seconds")
                    else None
                )
                result = await confirm_media_upload(
                    ConfirmMediaUploadRequest(
                        product_id=request.product_id,
                        merchant_id=request.merchant_id,
                        media_type=_from_media_type(request.media_type),
                        storage_key=request.storage_key,
                        public_url=request.public_url,
                        file_size=request.file_size,
                        width=width,
                        height=height,
                        duration_seconds=duration,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return _to_product_media(result)

    @inject
    async def DeleteMedia(
        self,
        request: catalog_pb2.DeleteMediaRequest,
        context: ServicerContext,
        delete_media: FromDishka[DeleteMediaUseCase],
    ) -> Empty:
        with _request_context(product_id=request.product_id):
            try:
                await delete_media(
                    DeleteMediaRequest(
                        product_id=request.product_id,
                        merchant_id=request.merchant_id,
                        media_id=request.media_id,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return Empty()

    @inject
    async def ReorderMedia(
        self,
        request: catalog_pb2.ReorderMediaRequest,
        context: ServicerContext,
        reorder_media: FromDishka[ReorderMediaUseCase],
    ) -> Empty:
        with _request_context(product_id=request.product_id):
            try:
                await reorder_media(
                    ReorderMediaRequest(
                        product_id=request.product_id,
                        merchant_id=request.merchant_id,
                        items=[
                            ReorderMediaItemDTO(
                                media_id=item.media_id, position=item.position
                            )
                            for item in request.items
                        ],
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return Empty()
