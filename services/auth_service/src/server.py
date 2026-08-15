import grpc
import structlog

from src.core.settings import Settings
from src.generated.auth.v1 import auth_pb2_grpc
from src.infrastructure.logging import setup_logging
from src.presentation.handlers import AuthServiceHandler
from src.presentation.interceptors import LoggingServerInterceptor

logger = structlog.get_logger()


async def start_server(host: str = "0.0.0.0", port: int = 50051) -> None:
    """Start the gRPC server for the AuthService."""

    setup_logging(Settings())
    logger.info("grpc.server_starting", host=host, port=port)

    server = grpc.aio.server(interceptors=[LoggingServerInterceptor()])
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceHandler(), server)
    server.add_insecure_port(f"{host}:{port}")
    try:
        await server.start()
    except Exception:
        logger.exception("grpc.server_start_failed", host=host, port=port)
        raise

    logger.info("grpc.server_started", host=host, port=port)

    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=None)
        logger.info("grpc.server_stopped")
