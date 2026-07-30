from fastapi import APIRouter

from src.routers.v1 import api_router as api_router_v1

api_router = APIRouter(prefix="/api")


@api_router.get("/healthcheck", tags=["healthcheck"])
async def health_check():
    """Check the health of the API."""
    return {"status": "ok"}


api_router.include_router(api_router_v1)
