import grpc

from src.generated.catalog.v1 import catalog_pb2_grpc
from src.presentation.grpc.handlers import CatalogServiceHandler


async def start_server(host: str = "0.0.0.0", port: int = 50052) -> None:
    """Start the gRPC server for the CatalogService."""

    server = grpc.aio.server()
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(
        CatalogServiceHandler(), server
    )
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()
