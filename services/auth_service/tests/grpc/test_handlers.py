"""gRPC handler tests using a real in-process gRPC server.

The server is wired to ``AuthServiceHandler`` with an injected fake unit-of-work
factory, so no database is required. These tests verify request/response
serialization and the gRPC error mapping (``context.abort``).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc
import pytest
from tests.conftest import FakeUnitOfWork, make_account, make_session

from src.generated.auth.v1 import auth_pb2, auth_pb2_grpc
from src.presentation.handlers import AuthServiceHandler
from src.usecase.base import AuthBaseUsecase

PASSWORD = "S3cr3t-pass!"
USER_EMAIL = "user@example.com"


async def _serve(uow_factory) -> tuple[auth_pb2_grpc.AuthServiceStub, AsyncIterator]:
    server = grpc.aio.server()
    handler = AuthServiceHandler(uow_factory=uow_factory)
    auth_pb2_grpc.add_AuthServiceServicer_to_server(handler, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
    stub = auth_pb2_grpc.AuthServiceStub(channel)

    async def stop():
        await channel.close()
        await server.stop(0)

    return stub, stop


@pytest.fixture
async def empty_stub() -> AsyncIterator[auth_pb2_grpc.AuthServiceStub]:
    """gRPC stub backed by an empty fake unit-of-work for each request."""
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    yield stub
    await stop()


async def test_signup_success_via_grpc(empty_stub):
    resp = await empty_stub.SignUp(
        auth_pb2.SignUpRequest(email="new@example.com", phone="+7", password=PASSWORD)
    )
    assert resp.access_token
    assert resp.refresh_token


async def test_signup_duplicate_aborts_with_already_exists():
    uow = FakeUnitOfWork(accounts=[make_account(email="dup@example.com")])
    stub, stop = await _serve(lambda: uow)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.SignUp(
                auth_pb2.SignUpRequest(
                    email="dup@example.com", phone="+7", password=PASSWORD
                )
            )
        assert exc_info.value.code() == grpc.StatusCode.ALREADY_EXISTS
        assert "already exists" in exc_info.value.details()
    finally:
        await stop()


async def test_login_success_via_grpc():
    account = make_account(password_hash=AuthBaseUsecase.hash_password(PASSWORD))
    session = make_session(user_id=account.id)
    uow = FakeUnitOfWork(accounts=[account], sessions=[session])
    stub, stop = await _serve(lambda: uow)
    try:
        resp = await stub.Login(
            auth_pb2.LoginRequest(email=account.email, password=PASSWORD)
        )
        assert resp.access_token
        assert resp.refresh_token
    finally:
        await stop()


async def test_login_invalid_credentials_aborts_unauthenticated():
    account = make_account(password_hash=AuthBaseUsecase.hash_password(PASSWORD))
    session = make_session(user_id=account.id)
    uow = FakeUnitOfWork(accounts=[account], sessions=[session])
    stub, stop = await _serve(lambda: uow)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.Login(
                auth_pb2.LoginRequest(email=account.email, password="wrong-password")
            )
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        await stop()


async def test_logout_success_via_grpc():
    account = make_account()
    session = make_session(user_id=account.id)
    uow = FakeUnitOfWork(accounts=[account], sessions=[session])
    stub, stop = await _serve(lambda: uow)
    try:
        resp = await stub.Logout(auth_pb2.LogoutRequest(session_id=str(session.id)))
        assert resp is not None
    finally:
        await stop()


async def test_logout_missing_session_aborts_not_found():
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.Logout(
                auth_pb2.LogoutRequest(
                    session_id="00000000-0000-0000-0000-000000000000"
                )
            )
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    finally:
        await stop()


async def test_refresh_success_via_grpc():
    account = make_account()
    session = make_session(user_id=account.id, is_active=True)
    uow = FakeUnitOfWork(accounts=[account], sessions=[session])
    stub, stop = await _serve(lambda: uow)
    try:
        token = AuthBaseUsecase.create_refresh_token(session.id)
        resp = await stub.Refresh(auth_pb2.RefreshRequest(refresh_token=token))
        assert resp.access_token
    finally:
        await stop()


async def test_refresh_invalid_token_aborts_unauthenticated(empty_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await empty_stub.Refresh(auth_pb2.RefreshRequest(refresh_token="not-a-jwt"))
    assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED


async def test_validate_valid_token_via_grpc():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = AuthBaseUsecase.create_access_token(user_id)
    stub, stop = await _serve(lambda: FakeUnitOfWork())
    try:
        resp = await stub.ValidateToken(
            auth_pb2.ValidateTokenRequest(access_token=token)
        )
        assert resp.valid is True
        assert resp.user_id == user_id
        assert resp.error_message == ""
    finally:
        await stop()


async def test_validate_invalid_token_via_grpc(empty_stub):
    resp = await empty_stub.ValidateToken(
        auth_pb2.ValidateTokenRequest(access_token="garbage.token.value")
    )
    assert resp.valid is False
    assert resp.user_id == ""
    assert resp.error_message == "Invalid token"


async def test_full_flow_via_grpc_signup_login_refresh_logout():
    """End-to-end flow through a single shared fake unit-of-work."""
    uow = FakeUnitOfWork()
    stub, stop = await _serve(lambda: uow)
    try:
        signup = await stub.SignUp(
            auth_pb2.SignUpRequest(email=USER_EMAIL, phone="+7", password=PASSWORD)
        )
        assert signup.access_token and signup.refresh_token

        login = await stub.Login(
            auth_pb2.LoginRequest(email=USER_EMAIL, password=PASSWORD)
        )
        assert login.access_token and login.refresh_token

        refresh = await stub.Refresh(
            auth_pb2.RefreshRequest(refresh_token=login.refresh_token)
        )
        assert refresh.access_token

        session = uow.session.records[0]
        logout = await stub.Logout(auth_pb2.LogoutRequest(session_id=str(session.id)))
        assert logout is not None
        assert session.is_active is False

        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.Refresh(
                auth_pb2.RefreshRequest(refresh_token=login.refresh_token)
            )
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        await stop()

        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
