from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import ApplicationError


def _application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(status_code=exc.http_code, content={"detail": exc.detail})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, _application_error_handler)
