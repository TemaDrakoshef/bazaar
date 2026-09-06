import grpc.aio

from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryMoveDTO,
    CategoryResult,
    CategoryUpdateDTO,
    ConfirmMediaUploadInput,
    DeleteMediaInput,
    MediaType,
    MediaUploadUrlInput,
    MediaUploadUrlResult,
    ProductCreateDTO,
    ProductListQuery,
    ProductListResult,
    ProductMediaResult,
    ProductResult,
    ProductUpdateDTO,
    ReorderMediaInput,
)
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc
from src.infrastructure.grpc.errors import translate_grpc_error
from src.infrastructure.grpc.logging import track_grpc_call


def _to_category_result(response: catalog_pb2.Category) -> CategoryResult:
    return CategoryResult(
        id=response.id,
        name=response.name,
        parent_id=response.parent_id or None,
        path=response.path,
        is_active=response.is_active,
        created_at=response.created_at.ToDatetime(),
        updated_at=response.updated_at.ToDatetime(),
    )


def _to_product_result(response: catalog_pb2.Product) -> ProductResult:
    return ProductResult(
        id=response.id,
        merchant_id=response.merchant_id,
        category_id=response.category_id,
        title=response.title,
        description=response.description,
        price=response.price,
        stock=response.stock,
        is_active=response.is_active,
        created_at=response.created_at.ToDatetime(),
        updated_at=response.updated_at.ToDatetime(),
        media=[_to_product_media_result(media) for media in response.media],
    )


def _to_product_media_result(response: catalog_pb2.ProductMedia) -> ProductMediaResult:
    return ProductMediaResult(
        id=response.id,
        product_id=response.product_id,
        media_type=_from_pb_media_type(response.media_type),
        url=response.url,
        position=response.position,
        width=response.width if response.HasField("width") else None,
        height=response.height if response.HasField("height") else None,
        duration_seconds=(
            response.duration_seconds if response.HasField("duration_seconds") else None
        ),
        file_size=response.file_size,
    )


def _from_pb_media_type(value: int) -> MediaType:
    name = catalog_pb2.MediaType.Name(value)
    if name == "MEDIA_TYPE_IMAGE":
        return MediaType.IMAGE
    return MediaType.VIDEO


def _to_pb_media_type(media_type: MediaType) -> int:
    return int(catalog_pb2.MediaType.Value(f"MEDIA_TYPE_{media_type.value}"))


class CatalogClient(AbstractCatalogGateway):
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = catalog_pb2_grpc.CatalogServiceStub(channel)

    async def create_category(self, data: CategoryCreateDTO) -> CategoryResult:
        async with track_grpc_call("catalog", "CreateCategory"):
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
        async with track_grpc_call("catalog", "ReadCategory"):
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
        async with track_grpc_call("catalog", "ReadListCategories"):
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
        if data.is_active is not None:
            request.is_active = data.is_active
        async with track_grpc_call("catalog", "UpdateCategory"):
            try:
                response = await self._stub.UpdateCategory(request)
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_category_result(response)

    async def delete_category(self, category_id: int) -> None:
        async with track_grpc_call("catalog", "DeleteCategory"):
            try:
                await self._stub.DeleteCategory(
                    catalog_pb2.CategoryIdRequest(category_id=category_id)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc

    async def move_category(
        self, category_id: int, data: CategoryMoveDTO
    ) -> CategoryResult:
        request = catalog_pb2.MoveCategoryRequest(category_id=category_id)
        if data.parent_id is not None:
            request.parent_id = data.parent_id
        async with track_grpc_call("catalog", "MoveCategory"):
            try:
                response = await self._stub.MoveCategory(request)
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_category_result(response)

    async def create_product(self, data: ProductCreateDTO) -> ProductResult:
        async with track_grpc_call("catalog", "CreateProduct"):
            try:
                response = await self._stub.CreateProduct(
                    catalog_pb2.CreateProductRequest(
                        merchant_id=data.merchant_id,
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
        async with track_grpc_call("catalog", "ReadProduct"):
            try:
                response = await self._stub.ReadProduct(
                    catalog_pb2.ProductIdRequest(product_id=product_id)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_product_result(response)

    async def read_list_products(self, query: ProductListQuery) -> ProductListResult:
        request = catalog_pb2.ListProductsRequest(
            limit=query.limit, offset=query.offset
        )
        if query.merchant_id is not None:
            request.merchant_id = query.merchant_id
        async with track_grpc_call("catalog", "ReadListProducts"):
            try:
                response = await self._stub.ReadListProducts(request)
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return ProductListResult(
            products=[_to_product_result(product) for product in response.products],
            count=response.count,
        )

    async def update_product(
        self, merchant_id: int, product_id: int, data: ProductUpdateDTO
    ) -> ProductResult:
        request = catalog_pb2.UpdateProductRequest(
            product_id=product_id, merchant_id=merchant_id
        )
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
        async with track_grpc_call("catalog", "UpdateProduct"):
            try:
                response = await self._stub.UpdateProduct(request)
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_product_result(response)

    async def delete_product(self, merchant_id: int, product_id: int) -> None:
        async with track_grpc_call("catalog", "DeleteProduct"):
            try:
                await self._stub.DeleteProduct(
                    catalog_pb2.DeleteProductRequest(
                        product_id=product_id, merchant_id=merchant_id
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc

    async def get_media_upload_url(
        self, data: MediaUploadUrlInput
    ) -> MediaUploadUrlResult:
        async with track_grpc_call("catalog", "GetMediaUploadUrl"):
            try:
                response = await self._stub.GetMediaUploadUrl(
                    catalog_pb2.GetMediaUploadUrlRequest(
                        product_id=data.product_id,
                        merchant_id=data.merchant_id,
                        media_type=_to_pb_media_type(data.media_type),
                        content_type=data.content_type,
                        file_size=data.file_size,
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return MediaUploadUrlResult(
            upload_url=response.upload_url,
            storage_key=response.storage_key,
            public_url=response.public_url,
        )

    async def confirm_media_upload(
        self, data: ConfirmMediaUploadInput
    ) -> ProductMediaResult:
        request = catalog_pb2.ConfirmMediaUploadRequest(
            product_id=data.product_id,
            merchant_id=data.merchant_id,
            media_type=_to_pb_media_type(data.media_type),
            storage_key=data.storage_key,
            public_url=data.public_url,
            file_size=data.file_size,
        )
        if data.width is not None:
            request.width = data.width
        if data.height is not None:
            request.height = data.height
        if data.duration_seconds is not None:
            request.duration_seconds = data.duration_seconds
        async with track_grpc_call("catalog", "ConfirmMediaUpload"):
            try:
                response = await self._stub.ConfirmMediaUpload(request)
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_product_media_result(response)

    async def delete_media(self, data: DeleteMediaInput) -> None:
        async with track_grpc_call("catalog", "DeleteMedia"):
            try:
                await self._stub.DeleteMedia(
                    catalog_pb2.DeleteMediaRequest(
                        product_id=data.product_id,
                        merchant_id=data.merchant_id,
                        media_id=data.media_id,
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc

    async def reorder_media(self, data: ReorderMediaInput) -> None:
        async with track_grpc_call("catalog", "ReorderMedia"):
            try:
                await self._stub.ReorderMedia(
                    catalog_pb2.ReorderMediaRequest(
                        product_id=data.product_id,
                        merchant_id=data.merchant_id,
                        items=[
                            catalog_pb2.ReorderMediaItem(
                                media_id=item.media_id, position=item.position
                            )
                            for item in data.items
                        ],
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
