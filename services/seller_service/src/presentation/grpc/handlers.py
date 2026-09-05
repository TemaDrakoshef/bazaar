from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

import structlog
from dishka.integrations.grpcio import FromDishka, inject
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext
from pydantic import ValidationError as PydanticValidationError
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.application.use_cases.create_merchant import CreateMerchantUseCase
from src.application.use_cases.get_merchant import GetMerchantUseCase
from src.application.use_cases.list_user_merchants import ListUserMerchantsUseCase
from src.application.use_cases.verify_access import VerifyAccessUseCase
from src.domain.dtos.merchant import MerchantCreateDTO, VerifyAccessDTO
from src.domain.entities.merchant import Merchant
from src.domain.exceptions import ApplicationError, ValidationError
from src.generated.seller.v1 import seller_pb2, seller_pb2_grpc

logger = structlog.get_logger()

_STATUS_TO_PB = {
    "ACTIVE": seller_pb2.MERCHANT_STATUS_ACTIVE,
    "PENDING_VERIFICATION": seller_pb2.MERCHANT_STATUS_PENDING_VERIFICATION,
}

_ROLE_TO_PB = {
    "OWNER": seller_pb2.MERCHANT_ROLE_OWNER,
    "MANAGER": seller_pb2.MERCHANT_ROLE_MANAGER,
    "VIEWER": seller_pb2.MERCHANT_ROLE_VIEWER,
}


def _to_timestamp(value: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(value)
    return timestamp


def _to_merchant(merchant: Merchant) -> seller_pb2.Merchant:
    return seller_pb2.Merchant(
        id=merchant.id,
        name=merchant.name,
        inn=merchant.inn,
        owner_user_id=merchant.owner_user_id,
        status=_STATUS_TO_PB[merchant.status],
        created_at=_to_timestamp(merchant.created_at),
    )


@contextmanager
def _request_context(**context: object) -> Iterator[None]:
    """Bind structured logging context for the duration of one RPC."""
    bind_contextvars(**context)
    try:
        yield
    finally:
        clear_contextvars()


async def _abort(context: ServicerContext, exc: Exception) -> None:
    """Log a failure and abort the RPC with the matching gRPC status."""
    if isinstance(exc, PydanticValidationError):
        error = ValidationError(str(exc.errors()[0].get("msg", "invalid input")))
    elif isinstance(exc, ApplicationError):
        error = exc
    else:
        logger.exception(
            "seller.unhandled_error",
            error_type=type(exc).__name__,
            error=repr(exc),
        )
        error = ApplicationError()
    logger.warning(
        "seller.request_failed",
        error_type=type(error).__name__,
        grpc_code=error.grpc_code.name,
        detail=error.detail,
    )
    await context.abort(error.grpc_code, error.detail)


class SellerServiceHandler(seller_pb2_grpc.SellerServiceServicer):
    @inject
    async def CreateMerchant(
        self,
        request: seller_pb2.CreateMerchantRequest,
        context: ServicerContext,
        create_merchant: FromDishka[CreateMerchantUseCase],
    ) -> seller_pb2.Merchant:
        with _request_context(name=request.name, inn=request.inn):
            try:
                result = await create_merchant(
                    MerchantCreateDTO(
                        name=request.name,
                        inn=request.inn,
                        user_id=request.user_id,
                    )
                )
            except Exception as exc:
                await _abort(context, exc)

            return _to_merchant(result)

    @inject
    async def GetMerchant(
        self,
        request: seller_pb2.GetMerchantRequest,
        context: ServicerContext,
        get_merchant: FromDishka[GetMerchantUseCase],
    ) -> seller_pb2.Merchant:
        with _request_context(merchant_id=request.merchant_id):
            try:
                result = await get_merchant(request.merchant_id)
            except Exception as exc:
                await _abort(context, exc)

            return _to_merchant(result)

    @inject
    async def ListUserMerchants(
        self,
        request: seller_pb2.ListUserMerchantsRequest,
        context: ServicerContext,
        list_user_merchants: FromDishka[ListUserMerchantsUseCase],
    ) -> seller_pb2.ListUserMerchantsResponse:
        with _request_context(user_id=request.user_id):
            try:
                result = await list_user_merchants(request.user_id)
            except Exception as exc:
                await _abort(context, exc)

            return seller_pb2.ListUserMerchantsResponse(
                merchants=[_to_merchant(merchant) for merchant in result]
            )

    @inject
    async def VerifyAccess(
        self,
        request: seller_pb2.VerifyAccessRequest,
        context: ServicerContext,
        verify_access: FromDishka[VerifyAccessUseCase],
    ) -> seller_pb2.VerifyAccessResponse:
        with _request_context(
            user_id=request.user_id, merchant_id=request.merchant_id
        ):
            result = await verify_access(
                VerifyAccessDTO(
                    user_id=request.user_id, merchant_id=request.merchant_id
                )
            )

            return seller_pb2.VerifyAccessResponse(
                allowed=result.allowed,
                role=_ROLE_TO_PB.get(result.role, seller_pb2.MERCHANT_ROLE_UNSPECIFIED),
            )
