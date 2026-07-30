from grpc import StatusCode


class ApplicationError(Exception):
    """Base class for application-specific errors."""

    grpc_code: StatusCode = StatusCode.INTERNAL
    message: str = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(self.detail)


class UserAlreadyExistsError(ApplicationError):
    """Raised when attempting to create a user that already exists."""

    grpc_code = StatusCode.ALREADY_EXISTS
    message = "user already exists"


class InvalidCredentialsError(ApplicationError):
    """Raised when provided credentials are invalid."""

    grpc_code = StatusCode.UNAUTHENTICATED
    message = "invalid credentials"


class SessionNotFoundError(ApplicationError):
    """Raised when a session is not found."""

    grpc_code = StatusCode.NOT_FOUND
    message = "session not found"


class InvalidRefreshTokenError(ApplicationError):
    """Raised when the provided refresh token is invalid."""

    grpc_code = StatusCode.UNAUTHENTICATED
    message = "invalid refresh token"


class SessionExpiredError(ApplicationError):
    """Raised when a session has expired."""

    grpc_code = StatusCode.UNAUTHENTICATED
    message = "session expired"
