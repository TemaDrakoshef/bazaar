from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from src.application.use_cases.catalog.create_category import CreateCategoryUseCase
from src.domain.dtos.catalog import CategoryCreateDTO
from src.presentation.schemas.catalog import CategoryCreateRequest, CategoryResponse

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/category")
@inject
async def create_category(
    data: CategoryCreateRequest,
    use_case: FromDishka[CreateCategoryUseCase],
) -> CategoryResponse:
    """Create a category via the catalog gRPC service."""
    result = await use_case.execute(CategoryCreateDTO(**data.model_dump()))
    return CategoryResponse(**result.model_dump())
