from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import settings
from src.infrastructure.di.container import ApiGatewayProvider
from src.presentation.api.router import api_router
from src.presentation.exception_handlers import register_exception_handlers


def create_app(*extra_providers: Provider) -> FastAPI:
    """Composition root: build the dishka container and the FastAPI app.

    ``extra_providers`` are registered after ``ApiGatewayProvider`` and may
    override its factories (dishka ``override=True``) — used by tests to
    replace ports with mocks.
    """
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
    app.include_router(api_router)
    register_exception_handlers(app)

    return app
