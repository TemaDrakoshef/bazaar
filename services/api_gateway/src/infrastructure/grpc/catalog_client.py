import grpc.aio

from src.domain.dtos.catalog import CategoryCreateDTO, CategoryResult
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc
from src.infrastructure.grpc.errors import translate_grpc_error


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
        return CategoryResult(
            id=response.id,
            name=response.name,
            path=response.path,
            is_active=response.is_active,
            created_at=response.created_at.ToDatetime(),
            updated_at=response.updated_at.ToDatetime(),
        )
