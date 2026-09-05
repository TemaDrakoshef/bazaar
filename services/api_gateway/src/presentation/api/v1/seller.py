from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from src.application.use_cases.catalog.create_product import CreateProductUseCase
from src.application.use_cases.catalog.delete_product import DeleteProductUseCase
from src.application.use_cases.catalog.read_list_products import (
    ReadListProductsUseCase,
)
from src.application.use_cases.catalog.update_product import UpdateProductUseCase
from src.domain.dtos.catalog import (
    ProductCreateDTO,
    ProductListQuery,
    ProductUpdateDTO,
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
