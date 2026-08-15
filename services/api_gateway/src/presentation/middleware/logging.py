from __future__ import annotations

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.stdlib import BoundLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, logger: BoundLogger | None = None) -> None:
        super().__init__(app)
        self._logger = logger or structlog.get_logger()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None

        start = time.perf_counter()
        bind_contextvars(
            http_method=method,
            http_path=path,
            client_ip=client_ip,
        )
        try:
            response = await call_next(request)
        except BaseException as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 3)
            clear_contextvars()
            self._logger.warning(
                "http.request.failed",
                method=method,
                path=path,
                error_type=type(exc).__name__,
                error=repr(exc),
                duration_ms=duration_ms,
            )
            raise
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        clear_contextvars()
        self._logger.info(
            "http.request.completed",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
