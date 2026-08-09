import grpc
from dishka import make_async_container
from dishka.integrations.grpcio import DishkaAioInterceptor, GrpcioProvider

from src.generated.catalog.v1 import catalog_pb2_grpc
from src.infrastructure.di.container import CatalogProvider
from src.presentation.grpc.handlers import CatalogServiceHandler


async def start_server(host: str = "0.0.0.0", port: int = 50052) -> None:
    """Start the gRPC server for the CatalogService."""

    container = make_async_container(CatalogProvider(), GrpcioProvider())
    server = grpc.aio.server(interceptors=[DishkaAioInterceptor(container)])
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(
        CatalogServiceHandler(), server
    )
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=None)
        await container.close()
