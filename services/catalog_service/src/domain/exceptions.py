from grpc import StatusCode


class ApplicationError(Exception):
    """Base class for application-specific errors."""

    grpc_code: StatusCode = StatusCode.INTERNAL
    message: str = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(self.detail)


class CategoryNotFoundError(ApplicationError):
    grpc_code = StatusCode.NOT_FOUND
    message = "category not found"
