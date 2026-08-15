import grpc
import structlog
from dishka import make_async_container
from dishka.integrations.grpcio import DishkaAioInterceptor, GrpcioProvider

from src.generated.catalog.v1 import catalog_pb2_grpc
from src.infrastructure.config.settings import Settings
from src.infrastructure.di.container import CatalogProvider
from src.infrastructure.logging import setup_logging
from src.presentation.grpc.handlers import CatalogServiceHandler
from src.presentation.grpc.interceptors import LoggingServerInterceptor

logger = structlog.get_logger()


async def start_server(host: str = "0.0.0.0", port: int = 50052) -> None:
    """Start the gRPC server for the CatalogService."""

    setup_logging(Settings())
    logger.info("grpc.server_starting", host=host, port=port)

    container = make_async_container(CatalogProvider(), GrpcioProvider())
    server = grpc.aio.server(
        interceptors=[LoggingServerInterceptor(), DishkaAioInterceptor(container)]
    )
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(
        CatalogServiceHandler(), server
    )
    server.add_insecure_port(f"{host}:{port}")
    try:
        await server.start()
    except Exception:
        logger.exception("grpc.server_start_failed", host=host, port=port)
        await container.close()
        raise

    logger.info("grpc.server_started", host=host, port=port)

    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=None)
        await container.close()
        logger.info("grpc.server_stopped")
