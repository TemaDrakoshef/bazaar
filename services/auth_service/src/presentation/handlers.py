from uuid import UUID

from grpc import ServicerContext

from src.domain.exceptions import ApplicationError
from src.generated.auth.v1 import auth_pb2, auth_pb2_grpc
from src.persistence.database import async_session_maker
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork, UowFactory
from src.usecase.login.request import LoginRequest
from src.usecase.login.usecase import LoginUsecase
from src.usecase.logout.request import LogoutRequest
from src.usecase.logout.usecase import LogoutUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.usecase import RefreshUsecase
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.usecase import SignUpUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.usecase import ValidateTokenUsecase


def _uow() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(async_session_maker)


class AuthServiceHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self, uow_factory: UowFactory | None = None) -> None:
        self._uow_factory = uow_factory or _uow

    async def SignUp(
        self, request: auth_pb2.SignUpRequest, context: ServicerContext
    ) -> auth_pb2.SignUpResponse:
        uc = SignUpUsecase(uow=self._uow_factory())
        try:
            result = await uc.execute(
                SignUpRequest(
                    email=request.email,
                    phone=request.phone,
                    password=request.password,
                )
            )
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return auth_pb2.SignUpResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
        )

    async def Login(
        self, request: auth_pb2.LoginRequest, context: ServicerContext
    ) -> auth_pb2.LoginResponse:
        uc = LoginUsecase(uow=self._uow_factory())
        try:
            result = await uc.execute(
                LoginRequest(email=request.email, password=request.password)
            )
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return auth_pb2.LoginResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
        )

    async def Logout(
        self, request: auth_pb2.LogoutRequest, context: ServicerContext
    ) -> auth_pb2.LogoutResponse:
        uc = LogoutUsecase(uow=self._uow_factory())
        try:
            await uc.execute(LogoutRequest(session_id=UUID(request.session_id)))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return auth_pb2.LogoutResponse()

    async def Refresh(
        self, request: auth_pb2.RefreshRequest, context: ServicerContext
    ) -> auth_pb2.RefreshResponse:
        uc = RefreshUsecase(uow=self._uow_factory())
        try:
            result = await uc.execute(
                RefreshRequest(refresh_token=request.refresh_token)
            )
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return auth_pb2.RefreshResponse(access_token=result.access_token)

    async def ValidateToken(
        self, request: auth_pb2.ValidateTokenRequest, context: ServicerContext
    ) -> auth_pb2.ValidateTokenResponse:
        uc = ValidateTokenUsecase()
        result = await uc.execute(
            ValidateTokenRequest(access_token=request.access_token)
        )

        msg = auth_pb2.ValidateTokenResponse(
            valid=result.valid,
            error_message=result.error_message,
        )
        if result.user_id is not None:
            msg.user_id = result.user_id
        return msg
