from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.clients.grpc_channels import Channels
from src.core.settings import settings
from src.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.channels = Channels()
    yield
    await app.state.channels.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name, version=settings.project_version, lifespan=lifespan
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    return app
