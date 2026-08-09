from datetime import datetime

from dishka.integrations.grpcio import FromDishka, inject
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext

from src.application.use_cases.create_product import CreateProductUseCase
from src.domain.dtos.product import ProductCreateDTO
from src.domain.exceptions import ApplicationError
from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc


def _to_timestamp(value: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(value)
    return timestamp


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

        return catalog_pb2.Product(
            id=result.id,
            category_id=result.category_id,
            title=result.title,
            description=result.description,
            price=result.price,
            stock=result.stock,
            is_active=result.is_active,
            created_at=_to_timestamp(result.created_at),
            updated_at=_to_timestamp(result.updated_at),
        )
