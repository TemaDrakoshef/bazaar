import grpc.aio
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.clients.auth_client import AuthClient
from src.exceptions import grpc_error_to_http

_bearer = HTTPBearer(auto_error=False)


def get_auth_client(request: Request) -> AuthClient:
    return AuthClient(request.app.state.channels.auth)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    auth_client: AuthClient = Depends(get_auth_client),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        response = await auth_client.validate_token(credentials.credentials)
    except grpc.aio.AioRpcError as exc:
        raise grpc_error_to_http(exc) from exc

    if not response.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.error_message or "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response.user_id
