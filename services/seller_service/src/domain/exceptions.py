from grpc import StatusCode


class ApplicationError(Exception):
    """Base class for application-specific errors."""

    grpc_code: StatusCode = StatusCode.INTERNAL
    message: str = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(self.detail)


class ValidationError(ApplicationError):
    grpc_code = StatusCode.INVALID_ARGUMENT
    message = "invalid input"


class MerchantNotFoundError(ApplicationError):
    grpc_code = StatusCode.NOT_FOUND
    message = "merchant not found"


class MerchantAlreadyExistsError(ApplicationError):
    grpc_code = StatusCode.ALREADY_EXISTS
    message = "merchant with this INN already exists"
