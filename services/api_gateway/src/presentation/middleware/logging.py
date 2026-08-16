from __future__ import annotations

import time
from uuid import uuid4

import structlog
from opentelemetry import trace
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
        request_id = request.headers.get(
            "x-request-id",
            str(uuid4()),
        )

        span = trace.get_current_span()
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, "032x")
        span_id = format(span_context.span_id, "016x")
        start = time.perf_counter()

        bind_contextvars(
            request_id=request_id,
            http_method=method,
            http_path=path,
            client_ip=client_ip,
            trace_id=trace_id,
            span_id=span_id,
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
                trace_id=trace_id,
                span_id=span_id,
            )
            raise
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        response.headers["X-Request-ID"] = request_id
        clear_contextvars()
        self._logger.info(
            "http.request.completed",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id,
        )
        return response
