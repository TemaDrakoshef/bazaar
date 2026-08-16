from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorClient

from src.infrastructure.config.settings import settings
from src.infrastructure.di.container import ApiGatewayProvider
from src.infrastructure.logging import setup_logging
from src.infrastructure.observability.telemetry import setup_telemetry
from src.presentation.api.router import api_router
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.middleware.logging import LoggingMiddleware


def create_app(*extra_providers: Provider) -> FastAPI:
    """Composition root: build the dishka container and the FastAPI app.

    ``extra_providers`` are registered after ``ApiGatewayProvider`` and may
    override its factories (dishka ``override=True``) — used by tests to
    replace ports with mocks.
    """
    setup_logging(settings)
    setup_telemetry()

    container = make_async_container(
        ApiGatewayProvider(), *extra_providers, FastapiProvider()
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with container:
            yield

    app = FastAPI(
        title=settings.project_name, version=settings.project_version, lifespan=lifespan
    )
    setup_dishka(container, app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    FastAPIInstrumentor.instrument_app(
        app,
        meter_provider=metrics.get_meter_provider(),
        excluded_urls="(metrics|healthz?|readyz|docs)",
    )
    GrpcAioInstrumentorClient().instrument()

    app.include_router(api_router)
    register_exception_handlers(app)

    return app
