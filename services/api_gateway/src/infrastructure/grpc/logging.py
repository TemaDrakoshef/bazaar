from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import grpc
import structlog

logger = structlog.get_logger()


@asynccontextmanager
async def track_grpc_call(service: str, method: str) -> AsyncIterator[None]:
    """Log one downstream gRPC call (client side) with duration and outcome."""
    start = time.perf_counter()
    try:
        yield
    except grpc.aio.AioRpcError as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        code = exc.code()
        logger.warning(
            "grpc.client.call_failed",
            service=service,
            method=method,
            code_name=code.name if code is not None else None,
            detail=exc.details(),
            duration_ms=duration_ms,
        )
        raise
    duration_ms = round((time.perf_counter() - start) * 1000, 3)
    logger.info(
        "grpc.client.call_completed",
        service=service,
        method=method,
        duration_ms=duration_ms,
    )
