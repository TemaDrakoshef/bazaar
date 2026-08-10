import grpc

from src.domain.exceptions import (
    ApplicationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    UnauthenticatedError,
    UnavailableError,
    ValidationError,
)

_GRPC_TO_ERROR: dict[grpc.StatusCode, type[ApplicationError]] = {
    grpc.StatusCode.NOT_FOUND: NotFoundError,
    grpc.StatusCode.INVALID_ARGUMENT: ValidationError,
    grpc.StatusCode.ALREADY_EXISTS: ConflictError,
    grpc.StatusCode.PERMISSION_DENIED: PermissionDeniedError,
    grpc.StatusCode.UNAUTHENTICATED: UnauthenticatedError,
    grpc.StatusCode.UNAVAILABLE: UnavailableError,
    grpc.StatusCode.DEADLINE_EXCEEDED: UnavailableError,
}


def translate_grpc_error(error: grpc.aio.AioRpcError) -> ApplicationError:
    """Map a gRPC ``AioRpcError`` to the corresponding domain exception."""
    error_type = _GRPC_TO_ERROR.get(error.code(), ApplicationError)
    return error_type(error.details())
