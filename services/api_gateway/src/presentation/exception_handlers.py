from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import ApplicationError

logger = structlog.get_logger()


def _application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    logger.warning(
        "http.request_failed",
        method=request.method,
        path=request.url.path,
        error_type=type(exc).__name__,
        http_code=exc.http_code,
        detail=exc.detail,
    )
    return JSONResponse(status_code=exc.http_code, content={"detail": exc.detail})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, _application_error_handler)
