import grpc
import structlog
from dishka import make_async_container
from dishka.integrations.grpcio import DishkaAioInterceptor, GrpcioProvider
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorClient

from src.generated.seller.v1 import seller_pb2_grpc
from src.infrastructure.config.settings import Settings
from src.infrastructure.di.container import SellerProvider
from src.infrastructure.logging import setup_logging
from src.infrastructure.observability.telemetry import setup_telemetry
from src.presentation.grpc.handlers import SellerServiceHandler
from src.presentation.grpc.interceptors import LoggingServerInterceptor

logger = structlog.get_logger()


async def start_server(host: str = "0.0.0.0", port: int = 50053) -> None:
    """Start the gRPC server for the SellerService."""
    settings = Settings()
    setup_logging(log_level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
    setup_telemetry(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    logger.info("grpc.server_starting", host=host, port=port)

    container = make_async_container(SellerProvider(), GrpcioProvider())
    server = grpc.aio.server(
        interceptors=[LoggingServerInterceptor(), DishkaAioInterceptor(container)]
    )
    seller_pb2_grpc.add_SellerServiceServicer_to_server(SellerServiceHandler(), server)
    GrpcAioInstrumentorClient().instrument()
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
