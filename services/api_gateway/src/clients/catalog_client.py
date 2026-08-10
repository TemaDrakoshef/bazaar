import grpc.aio

from src.domain.dtos.catalog import CategoryCreateDTO
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc


class CatalogClient:
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = catalog_pb2_grpc.CatalogServiceStub(channel)

    async def create_category(
        self,
        data: CategoryCreateDTO,
    ) -> catalog_pb2.Category:
        return await self._stub.CreateCategory(
            catalog_pb2.CreateCategoryRequest(name=data.name, parent_id=data.parent_id)
        )
