from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any, cast

import grpc
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.stdlib import BoundLogger


class LoggingServerInterceptor(grpc.aio.ServerInterceptor):
    """Log each gRPC call at the transport layer.

    Emits one ``grpc.request.completed`` (info) or ``grpc.request.failed``
    (warning) event per RPC with the fully-qualified method name and call
    duration, and binds the method into the structured logging context so
    downstream (handler / use case) records automatically carry it.
    """

    def __init__(self, logger: BoundLogger | None = None) -> None:
        self._logger = logger or structlog.get_logger()

    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        handler = await continuation(handler_call_details)
        if handler is None:
            return None

        method = handler_call_details.method

        def _wrap(
            behavior: Callable[..., Awaitable[Any]] | None,
        ) -> Callable[..., Awaitable[Any]] | None:
            if behavior is None:
                return None

            async def wrapper(request_or_iterator: Any, context: Any) -> Any:
                bind_contextvars(grpc_method=method)
                start = time.perf_counter()
                try:
                    response = await behavior(request_or_iterator, context)
                except BaseException as exc:
                    duration_ms = round((time.perf_counter() - start) * 1000, 3)
                    self._logger.warning(
                        "grpc.request.failed",
                        method=method,
                        error_type=type(exc).__name__,
                        error=repr(exc),
                        duration_ms=duration_ms,
                    )
                    clear_contextvars()
                    raise
                duration_ms = round((time.perf_counter() - start) * 1000, 3)
                clear_contextvars()
                self._logger.info(
                    "grpc.request.completed",
                    method=method,
                    duration_ms=duration_ms,
                )
                return response

            return wrapper

        concrete = cast(Any, handler)
        wrapped = concrete._replace(
            unary_unary=_wrap(concrete.unary_unary),
            unary_stream=_wrap(concrete.unary_stream),
            stream_unary=_wrap(concrete.stream_unary),
            stream_stream=_wrap(concrete.stream_stream),
        )
        return cast(grpc.RpcMethodHandler, wrapped)
