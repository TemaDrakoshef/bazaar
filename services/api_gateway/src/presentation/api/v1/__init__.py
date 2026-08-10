from fastapi import APIRouter

from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.catalog import router as catalog_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(catalog_router)
