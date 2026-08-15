from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from src.application.use_cases.catalog.create_category import CreateCategoryUseCase
from src.application.use_cases.catalog.create_product import CreateProductUseCase
from src.application.use_cases.catalog.delete_category import DeleteCategoryUseCase
from src.application.use_cases.catalog.delete_product import DeleteProductUseCase
from src.application.use_cases.catalog.move_category import MoveCategoryUseCase
from src.application.use_cases.catalog.read_category import ReadCategoryUseCase
from src.application.use_cases.catalog.read_list_categories import (
    ReadListCategoriesUseCase,
)
from src.application.use_cases.catalog.read_list_products import (
    ReadListProductsUseCase,
)
from src.application.use_cases.catalog.read_product import ReadProductUseCase
from src.application.use_cases.catalog.update_category import UpdateCategoryUseCase
from src.application.use_cases.catalog.update_product import UpdateProductUseCase
from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryMoveDTO,
    CategoryUpdateDTO,
    ProductCreateDTO,
    ProductListQuery,
    ProductUpdateDTO,
)
from src.presentation.schemas.catalog import (
    CategoryCreateRequest,
    CategoryMoveRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/category", response_model=CategoryResponse, status_code=201)
@inject
async def create_category(
    data: CategoryCreateRequest,
    use_case: FromDishka[CreateCategoryUseCase],
) -> CategoryResponse:
    """Create a category via the catalog gRPC service."""
    result = await use_case.execute(CategoryCreateDTO(**data.model_dump()))
    return CategoryResponse(**result.model_dump())


@router.get("/category/{category_id}", response_model=CategoryResponse)
@inject
async def read_category(
    category_id: int,
    use_case: FromDishka[ReadCategoryUseCase],
) -> CategoryResponse:
    """Read a single category by id."""
    result = await use_case.execute(category_id)
    return CategoryResponse(**result.model_dump())


@router.get("/category", response_model=list[CategoryResponse])
@inject
async def read_list_categories(
    use_case: FromDishka[ReadListCategoriesUseCase],
    limit: int = 20,
    offset: int = 0,
) -> list[CategoryResponse]:
    """List categories."""
    result = await use_case.execute(CategoryListQuery(limit=limit, offset=offset))
    return [CategoryResponse(**category.model_dump()) for category in result]


@router.patch("/category/{category_id}", response_model=CategoryResponse)
@inject
async def update_category(
    category_id: int,
    data: CategoryUpdateRequest,
    use_case: FromDishka[UpdateCategoryUseCase],
) -> CategoryResponse:
    """Update a category by id."""
    result = await use_case.execute(
        category_id, CategoryUpdateDTO(**data.model_dump(exclude_none=True))
    )
    return CategoryResponse(**result.model_dump())


@router.delete("/category/{category_id}", status_code=204)
@inject
async def delete_category(
    category_id: int,
    use_case: FromDishka[DeleteCategoryUseCase],
) -> None:
    """Delete a category by id."""
    await use_case.execute(category_id)


@router.patch("/category/{category_id}/move", response_model=CategoryResponse)
@inject
async def move_category(
    category_id: int,
    data: CategoryMoveRequest,
    use_case: FromDishka[MoveCategoryUseCase],
) -> CategoryResponse:
    """Move a category under a new parent (or to the root when parent_id is absent)."""
    result = await use_case.execute(
        category_id, CategoryMoveDTO(**data.model_dump(exclude_none=True))
    )
    return CategoryResponse(**result.model_dump())


@router.post("/product", response_model=ProductResponse, status_code=201)
@inject
async def create_product(
    data: ProductCreateRequest,
    use_case: FromDishka[CreateProductUseCase],
) -> ProductResponse:
    """Create a product via the catalog gRPC service."""
    result = await use_case.execute(ProductCreateDTO(**data.model_dump()))
    return ProductResponse(**result.model_dump())


@router.get("/product/{product_id}", response_model=ProductResponse)
@inject
async def read_product(
    product_id: int,
    use_case: FromDishka[ReadProductUseCase],
) -> ProductResponse:
    """Read a single product by id."""
    result = await use_case.execute(product_id)
    return ProductResponse(**result.model_dump())


@router.get("/product", response_model=ProductListResponse)
@inject
async def read_list_products(
    use_case: FromDishka[ReadListProductsUseCase],
    limit: int = 20,
    offset: int = 0,
) -> ProductListResponse:
    """List products."""
    result = await use_case.execute(ProductListQuery(limit=limit, offset=offset))
    return ProductListResponse(
        products=[
            ProductResponse(**product.model_dump()) for product in result.products
        ],
        count=result.count,
    )


@router.patch("/product/{product_id}", response_model=ProductResponse)
@inject
async def update_product(
    product_id: int,
    data: ProductUpdateRequest,
    use_case: FromDishka[UpdateProductUseCase],
) -> ProductResponse:
    """Update a product by id."""
    result = await use_case.execute(
        product_id, ProductUpdateDTO(**data.model_dump(exclude_none=True))
    )
    return ProductResponse(**result.model_dump())


@router.delete("/product/{product_id}", status_code=204)
@inject
async def delete_product(
    product_id: int,
    use_case: FromDishka[DeleteProductUseCase],
) -> None:
    """Delete a product by id."""
    await use_case.execute(product_id)
