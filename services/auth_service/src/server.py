import grpc

from src.generated.auth.v1 import auth_pb2_grpc
from src.presentation.handlers import AuthServiceHandler


async def start_server(host: str = "0.0.0.0", port: int = 50051) -> None:
    """Start the gRPC server for the AuthService."""

    server = grpc.aio.server()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceHandler(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()
