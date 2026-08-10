import grpc.aio

from src.infrastructure.config.settings import Settings


class Channels:
    """Owns all gRPC async channels for the lifetime of the application."""

    def __init__(self, settings: Settings) -> None:
        self.auth = grpc.aio.insecure_channel(settings.auth_address)
        self.catalog = grpc.aio.insecure_channel(settings.catalog_address)

    async def close(self) -> None:
        await self.auth.close()
        await self.catalog.close()
