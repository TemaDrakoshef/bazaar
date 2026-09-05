"""gRPC handler tests for the SellerService using an in-process server."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc
import pytest

from src.application.use_cases.create_merchant import CreateMerchantUseCase
from src.application.use_cases.get_merchant import GetMerchantUseCase
from src.application.use_cases.list_user_merchants import ListUserMerchantsUseCase
from src.application.use_cases.verify_access import VerifyAccessUseCase
from src.domain.dtos.merchant import MerchantCreateDTO, VerifyAccessDTO
from src.generated.seller.v1 import seller_pb2, seller_pb2_grpc
from src.presentation.grpc.handlers import _abort, _to_merchant
from tests.conftest import FakeUnitOfWork, make_member, make_merchant

pytestmark = pytest.mark.unit


class FakeSellerServiceHandler(seller_pb2_grpc.SellerServiceServicer):
    def __init__(self, uow_factory=None):
        self._uow_factory = uow_factory or (lambda: FakeUnitOfWork())

    async def CreateMerchant(self, request, context):
        uc = CreateMerchantUseCase(self._uow_factory())
        try:
            result = await uc(
                MerchantCreateDTO(
                    name=request.name,
                    inn=request.inn,
                    user_id=request.user_id,
                )
            )
        except Exception as exc:
            await _abort(context, exc)
        return _to_merchant(result)

    async def GetMerchant(self, request, context):
        uc = GetMerchantUseCase(self._uow_factory())
        try:
            result = await uc(request.merchant_id)
        except Exception as exc:
            await _abort(context, exc)
        return _to_merchant(result)

    async def ListUserMerchants(self, request, context):
        uc = ListUserMerchantsUseCase(self._uow_factory())
        try:
            result = await uc(request.user_id)
        except Exception as exc:
            await _abort(context, exc)
        return seller_pb2.ListUserMerchantsResponse(
            merchants=[_to_merchant(merchant) for merchant in result]
        )

    async def VerifyAccess(self, request, context):
        uc = VerifyAccessUseCase(self._uow_factory())
        result = await uc(
            VerifyAccessDTO(user_id=request.user_id, merchant_id=request.merchant_id)
        )
        return seller_pb2.VerifyAccessResponse(
            allowed=result.allowed,
            role=seller_pb2.MERCHANT_ROLE_MANAGER if result.role == "MANAGER"
            else seller_pb2.MERCHANT_ROLE_OWNER if result.role == "OWNER"
            else seller_pb2.MERCHANT_ROLE_VIEWER if result.role == "VIEWER"
            else seller_pb2.MERCHANT_ROLE_UNSPECIFIED,
        )


async def _serve(
    uow_factory,
) -> tuple[seller_pb2_grpc.SellerServiceStub, AsyncIterator]:
    server = grpc.aio.server()
    handler = FakeSellerServiceHandler(uow_factory=uow_factory)
    seller_pb2_grpc.add_SellerServiceServicer_to_server(handler, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
    stub = seller_pb2_grpc.SellerServiceStub(channel)

    async def stop():
        await channel.close()
        await server.stop(0)

    return stub, stop


async def test_create_merchant_via_grpc():
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    try:
        resp = await stub.CreateMerchant(
            seller_pb2.CreateMerchantRequest(
                name="shop", inn="7703456789", user_id="user-1"
            )
        )
        assert resp.id == 1
        assert resp.name == "shop"
        assert resp.status == seller_pb2.MERCHANT_STATUS_ACTIVE
        assert resp.owner_user_id == "user-1"
    finally:
        await stop()


async def test_create_merchant_invalid_inn_aborts_invalid_argument():
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.CreateMerchant(
                seller_pb2.CreateMerchantRequest(
                    name="shop", inn="not-an-inn", user_id="user-1"
                )
            )
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    finally:
        await stop()


async def test_create_merchant_duplicate_inn_aborts_already_exists():
    existing = make_merchant(id_=1, inn="7703456789")
    stub, stop = await _serve(lambda: FakeUnitOfWork(merchants=[existing]))
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.CreateMerchant(
                seller_pb2.CreateMerchantRequest(
                    name="other", inn="7703456789", user_id="user-2"
                )
            )
        assert exc_info.value.code() == grpc.StatusCode.ALREADY_EXISTS
    finally:
        await stop()


async def test_get_merchant_via_grpc():
    merchant = make_merchant(id_=7, name="shop")
    stub, stop = await _serve(lambda: FakeUnitOfWork(merchants=[merchant]))
    try:
        resp = await stub.GetMerchant(seller_pb2.GetMerchantRequest(merchant_id=7))
        assert resp.id == 7
        assert resp.name == "shop"
    finally:
        await stop()


async def test_get_merchant_missing_aborts_not_found():
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.GetMerchant(seller_pb2.GetMerchantRequest(merchant_id=999))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    finally:
        await stop()


async def test_list_user_merchants_via_grpc():
    merch_a = make_merchant(id_=1, name="A")
    merch_b = make_merchant(id_=2, name="B")
    members = [
        make_member(id_=1, merchant_id=1, user_id="user-1"),
        make_member(id_=2, merchant_id=2, user_id="user-1"),
    ]
    stub, stop = await _serve(
        lambda: FakeUnitOfWork(merchants=[merch_a, merch_b], members=members)
    )
    try:
        resp = await stub.ListUserMerchants(
            seller_pb2.ListUserMerchantsRequest(user_id="user-1")
        )
        assert [m.id for m in resp.merchants] == [1, 2]
    finally:
        await stop()


async def test_verify_access_allowed_via_grpc():
    merchant = make_merchant(id_=1)
    member = make_member(merchant_id=1, user_id="user-1", role="MANAGER")
    stub, stop = await _serve(
        lambda: FakeUnitOfWork(merchants=[merchant], members=[member])
    )
    try:
        resp = await stub.VerifyAccess(
            seller_pb2.VerifyAccessRequest(user_id="user-1", merchant_id=1)
        )
        assert resp.allowed is True
    finally:
        await stop()


async def test_verify_access_denied_via_grpc():
    merchant = make_merchant(id_=1)
    stub, stop = await _serve(lambda: FakeUnitOfWork(merchants=[merchant]))
    try:
        resp = await stub.VerifyAccess(
            seller_pb2.VerifyAccessRequest(user_id="stranger", merchant_id=1)
        )
        assert resp.allowed is False
    finally:
        await stop()
