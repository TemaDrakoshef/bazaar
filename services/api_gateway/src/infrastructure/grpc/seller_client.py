import grpc.aio

from src.domain.dtos.seller import (
    MerchantCreateInput,
    MerchantResult,
    VerifyAccessInput,
    VerifyAccessResult,
)
from src.domain.interfaces.seller_gateway import AbstractSellerGateway
from src.generated.seller.v1 import seller_pb2, seller_pb2_grpc
from src.infrastructure.grpc.errors import translate_grpc_error
from src.infrastructure.grpc.logging import track_grpc_call

_STATUS_TO_STR = {
    seller_pb2.MERCHANT_STATUS_ACTIVE: "ACTIVE",
    seller_pb2.MERCHANT_STATUS_PENDING_VERIFICATION: "PENDING_VERIFICATION",
}

_ROLE_TO_STR = {
    seller_pb2.MERCHANT_ROLE_OWNER: "OWNER",
    seller_pb2.MERCHANT_ROLE_MANAGER: "MANAGER",
    seller_pb2.MERCHANT_ROLE_VIEWER: "VIEWER",
}


def _to_merchant_result(response: seller_pb2.Merchant) -> MerchantResult:
    return MerchantResult(
        id=response.id,
        name=response.name,
        inn=response.inn,
        owner_user_id=response.owner_user_id,
        status=_STATUS_TO_STR.get(response.status, "UNKNOWN"),
        created_at=response.created_at.ToDatetime(),
    )


class SellerClient(AbstractSellerGateway):
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self._stub = seller_pb2_grpc.SellerServiceStub(channel)

    async def create_merchant(self, data: MerchantCreateInput) -> MerchantResult:
        async with track_grpc_call("seller", "CreateMerchant"):
            try:
                response = await self._stub.CreateMerchant(
                    seller_pb2.CreateMerchantRequest(
                        name=data.name, inn=data.inn, user_id=data.user_id
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return _to_merchant_result(response)

    async def list_user_merchants(self, user_id: str) -> list[MerchantResult]:
        async with track_grpc_call("seller", "ListUserMerchants"):
            try:
                response = await self._stub.ListUserMerchants(
                    seller_pb2.ListUserMerchantsRequest(user_id=user_id)
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return [_to_merchant_result(merchant) for merchant in response.merchants]

    async def verify_access(self, data: VerifyAccessInput) -> VerifyAccessResult:
        async with track_grpc_call("seller", "VerifyAccess"):
            try:
                response = await self._stub.VerifyAccess(
                    seller_pb2.VerifyAccessRequest(
                        user_id=data.user_id, merchant_id=data.merchant_id
                    )
                )
            except grpc.aio.AioRpcError as exc:
                raise translate_grpc_error(exc) from exc
        return VerifyAccessResult(
            allowed=response.allowed,
            role=_ROLE_TO_STR.get(response.role, ""),
        )
