class ApplicationError(Exception):
    """Base class for application-specific errors.

    ``http_code`` is consumed by the presentation layer to build an HTTP reply.
    """

    http_code: int = 500
    message: str = "application error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.message
        super().__init__(self.detail)


class ValidationError(ApplicationError):
    http_code = 422
    message = "invalid input"


class UnauthenticatedError(ApplicationError):
    http_code = 401
    message = "unauthenticated"


class PermissionDeniedError(ApplicationError):
    http_code = 403
    message = "permission denied"


class NotFoundError(ApplicationError):
    http_code = 404
    message = "not found"


class ConflictError(ApplicationError):
    http_code = 409
    message = "conflict"


class UnavailableError(ApplicationError):
    http_code = 503
    message = "upstream service unavailable"
