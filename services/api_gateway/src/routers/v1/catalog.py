import grpc.aio
from fastapi import APIRouter, Depends

from src.clients.catalog_client import CatalogClient
from src.dependencies import get_catalog_client
from src.domain.dtos.catalog import CategoryCreateDTO
from src.exceptions import grpc_error_to_http
from src.generated.catalog.v1.catalog_pb2 import Category
from src.schemas.catalog import CategoryCreateRequest, CategoryResponse

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/category")
async def create_category(
    data: CategoryCreateRequest,
    catalog_client: CatalogClient = Depends(get_catalog_client),
) -> CategoryResponse:
    """Create a category via the catalog gRPC service."""
    try:
        new_category = CategoryCreateDTO(name=data.name, parent_id=data.parent_id)
        resp: Category = await catalog_client.create_category(data=new_category)
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc
    return CategoryResponse(
        id=resp.id,
        name=resp.name,
        path=resp.path,
        is_active=resp.is_active,
        created_at=resp.created_at.ToDatetime(),
        updated_at=resp.updated_at.ToDatetime(),
    )
