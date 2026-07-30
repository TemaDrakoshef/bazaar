import grpc
from fastapi import HTTPException

_GRPC_TO_HTTP: dict[grpc.StatusCode, int] = {
    grpc.StatusCode.NOT_FOUND: 404,
    grpc.StatusCode.INVALID_ARGUMENT: 422,
    grpc.StatusCode.ALREADY_EXISTS: 409,
    grpc.StatusCode.PERMISSION_DENIED: 403,
    grpc.StatusCode.UNAUTHENTICATED: 401,
}


def grpc_error_to_http(error: grpc.aio.AioRpcError) -> HTTPException:
    """Map a gRPC AioRpcError to a FastAPI HTTPException."""
    status_code = _GRPC_TO_HTTP.get(error.code(), 500)
    detail = error.details() or str(error.code())
    return HTTPException(status_code=status_code, detail=detail)
