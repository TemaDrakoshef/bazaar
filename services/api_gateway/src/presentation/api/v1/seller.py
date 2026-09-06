from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from src.application.use_cases.catalog.confirm_media_upload import (
    ConfirmMediaUploadUseCase,
)
from src.application.use_cases.catalog.create_product import CreateProductUseCase
from src.application.use_cases.catalog.delete_media import DeleteMediaUseCase
from src.application.use_cases.catalog.delete_product import DeleteProductUseCase
from src.application.use_cases.catalog.get_media_upload_url import (
    GetMediaUploadUrlUseCase,
)
from src.application.use_cases.catalog.read_list_products import (
    ReadListProductsUseCase,
)
from src.application.use_cases.catalog.read_product import ReadProductUseCase
from src.application.use_cases.catalog.reorder_media import ReorderMediaUseCase
from src.application.use_cases.catalog.update_product import UpdateProductUseCase
from src.domain.dtos.catalog import (
    ConfirmMediaUploadInput,
    DeleteMediaInput,
    MediaUploadUrlInput,
    ProductCreateDTO,
    ProductListQuery,
    ProductUpdateDTO,
    ReorderMediaInput,
    ReorderMediaItemInput,
)
from src.domain.exceptions import (
    ConflictError,
    MediaUploadConflictError,
    PermissionDeniedError,
)
from src.presentation.api.dependencies import (
    MerchantContext,
    get_current_merchant_context,
)
from src.presentation.schemas.catalog import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from src.presentation.schemas.seller_media import (
    ConfirmUploadSchemaIn,
    GetUploadUrlSchemaIn,
    GetUploadUrlSchemaOut,
    MediaResponse,
    ReorderMediaSchemaIn,
)

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/products", response_model=ProductResponse, status_code=201)
@inject
async def create_product(
    data: ProductCreateRequest,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[CreateProductUseCase],
) -> ProductResponse:
    """Create a product owned by the merchant from ``X-Merchant-ID``."""
    result = await use_case.execute(
        ProductCreateDTO(merchant_id=context.merchant_id, **data.model_dump())
    )
    return ProductResponse(**result.model_dump())


@router.get("/products", response_model=ProductListResponse)
@inject
async def list_products(
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[ReadListProductsUseCase],
    limit: int = 20,
    offset: int = 0,
) -> ProductListResponse:
    """List the merchant's own products (stock table)."""
    result = await use_case.execute(
        ProductListQuery(limit=limit, offset=offset, merchant_id=context.merchant_id)
    )
    return ProductListResponse(
        products=[
            ProductResponse(**product.model_dump()) for product in result.products
        ],
        count=result.count,
    )


@router.patch("/products/{product_id}", response_model=ProductResponse)
@inject
async def update_product(
    product_id: int,
    data: ProductUpdateRequest,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[UpdateProductUseCase],
) -> ProductResponse:
    """Update a product owned by the merchant from ``X-Merchant-ID``."""
    result = await use_case.execute(
        context.merchant_id,
        product_id,
        ProductUpdateDTO(**data.model_dump(exclude_none=True)),
    )
    return ProductResponse(**result.model_dump())


@router.delete("/products/{product_id}", status_code=204)
@inject
async def delete_product(
    product_id: int,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[DeleteProductUseCase],
) -> None:
    """Delete a product owned by the merchant from ``X-Merchant-ID``."""
    await use_case.execute(context.merchant_id, product_id)


@router.get("/products/{product_id}", response_model=ProductResponse)
@inject
async def read_owned_product(
    product_id: int,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[ReadProductUseCase],
) -> ProductResponse:
    """Read one of the merchant's own products including its media."""
    result = await use_case.execute(product_id)
    if result.merchant_id != context.merchant_id:
        raise PermissionDeniedError("no access to the requested product")
    return ProductResponse(**result.model_dump())


@router.post(
    "/products/{product_id}/media/upload-url",
    response_model=GetUploadUrlSchemaOut,
)
@inject
async def get_media_upload_url(
    product_id: int,
    data: GetUploadUrlSchemaIn,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[GetMediaUploadUrlUseCase],
) -> GetUploadUrlSchemaOut:
    """Return a presigned PUT URL for a direct upload to MinIO."""
    try:
        result = await use_case.execute(
            MediaUploadUrlInput(
                product_id=product_id,
                merchant_id=context.merchant_id,
                media_type=data.media_type,
                content_type=data.content_type,
                file_size=data.file_size,
            )
        )
    except ConflictError as exc:
        raise MediaUploadConflictError(exc.detail) from exc
    return GetUploadUrlSchemaOut(**result.model_dump())


@router.post(
    "/products/{product_id}/media/confirm",
    response_model=MediaResponse,
    status_code=201,
)
@inject
async def confirm_media_upload(
    product_id: int,
    data: ConfirmUploadSchemaIn,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[ConfirmMediaUploadUseCase],
) -> MediaResponse:
    """Register an uploaded object as product media."""
    result = await use_case.execute(
        ConfirmMediaUploadInput(
            product_id=product_id,
            merchant_id=context.merchant_id,
            media_type=data.media_type,
            storage_key=data.storage_key,
            public_url=data.public_url,
            file_size=data.file_size,
            width=data.width,
            height=data.height,
            duration_seconds=data.duration_seconds,
        )
    )
    return MediaResponse(**result.model_dump())


@router.delete("/products/{product_id}/media/{media_id}", status_code=204)
@inject
async def delete_media(
    product_id: int,
    media_id: int,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[DeleteMediaUseCase],
) -> None:
    """Delete a media record and its object from MinIO."""
    await use_case.execute(
        DeleteMediaInput(
            product_id=product_id,
            merchant_id=context.merchant_id,
            media_id=media_id,
        )
    )


@router.patch("/products/{product_id}/media/reorder", status_code=204)
@inject
async def reorder_media(
    product_id: int,
    data: ReorderMediaSchemaIn,
    context: Annotated[MerchantContext, Depends(get_current_merchant_context)],
    use_case: FromDishka[ReorderMediaUseCase],
) -> None:
    """Batch-update media positions for a product."""
    await use_case.execute(
        ReorderMediaInput(
            product_id=product_id,
            merchant_id=context.merchant_id,
            items=[
                ReorderMediaItemInput(media_id=item.media_id, position=item.position)
                for item in data.items
            ],
        )
    )
