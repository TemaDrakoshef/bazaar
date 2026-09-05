"""Unit tests for seller use cases against an in-memory fake unit of work."""

from __future__ import annotations

import pytest

from src.application.use_cases.create_merchant import CreateMerchantUseCase
from src.application.use_cases.get_merchant import GetMerchantUseCase
from src.application.use_cases.list_user_merchants import ListUserMerchantsUseCase
from src.application.use_cases.verify_access import VerifyAccessUseCase
from src.domain.dtos.merchant import MerchantCreateDTO, VerifyAccessDTO
from src.domain.exceptions import MerchantAlreadyExistsError, MerchantNotFoundError
from tests.conftest import FakeUnitOfWork, make_member, make_merchant

pytestmark = pytest.mark.unit


async def test_create_merchant_with_owner_membership():
    uow = FakeUnitOfWork()

    result = await CreateMerchantUseCase(uow)(
        MerchantCreateDTO(name="shop", inn="7703456789", user_id="user-1")
    )

    assert result.id == 1
    assert result.name == "shop"
    assert result.status == "ACTIVE"
    owner = uow.member.records[0]
    assert owner.merchant_id == result.id
    assert owner.user_id == "user-1"
    assert owner.role == "OWNER"
    assert owner.is_active is True


async def test_create_merchant_duplicate_inn_rejected():
    merchant = make_merchant(id_=1, inn="7703456789")
    uow = FakeUnitOfWork(merchants=[merchant])

    with pytest.raises(MerchantAlreadyExistsError):
        await CreateMerchantUseCase(uow)(
            MerchantCreateDTO(name="other", inn="7703456789", user_id="user-2")
        )


async def test_get_merchant_found():
    merchant = make_merchant(id_=7, name="shop")
    uow = FakeUnitOfWork(merchants=[merchant])

    result = await GetMerchantUseCase(uow)(7)

    assert result.id == 7
    assert result.name == "shop"


async def test_get_merchant_missing_raises_not_found():
    uow = FakeUnitOfWork()

    with pytest.raises(MerchantNotFoundError):
        await GetMerchantUseCase(uow)(999)


async def test_list_user_merchants_returns_active_ones():
    merch_a = make_merchant(id_=1, name="A")
    merch_b = make_merchant(id_=2, name="B")
    merch_inactive = make_merchant(id_=3, name="C", status="PENDING_VERIFICATION")
    uow = FakeUnitOfWork(
        merchants=[merch_a, merch_b, merch_inactive],
        members=[
            make_member(id_=1, merchant_id=1, user_id="user-1"),
            make_member(id_=2, merchant_id=2, user_id="user-1"),
            make_member(id_=3, merchant_id=3, user_id="user-1"),
        ],
    )

    result = await ListUserMerchantsUseCase(uow)("user-1")

    assert [m.id for m in result] == [1, 2]


async def test_list_user_merchants_skips_inactive_membership():
    merch_a = make_merchant(id_=1, name="A")
    merch_b = make_merchant(id_=2, name="B")
    uow = FakeUnitOfWork(
        merchants=[merch_a, merch_b],
        members=[
            make_member(id_=1, merchant_id=1, user_id="user-1", is_active=True),
            make_member(id_=2, merchant_id=2, user_id="user-1", is_active=False),
        ],
    )

    result = await ListUserMerchantsUseCase(uow)("user-1")

    assert [m.id for m in result] == [1]


async def test_verify_access_allows_active_member():
    merchant = make_merchant(id_=1)
    member = make_member(merchant_id=1, user_id="user-1", role="MANAGER")
    uow = FakeUnitOfWork(merchants=[merchant], members=[member])

    result = await VerifyAccessUseCase(uow)(
        VerifyAccessDTO(user_id="user-1", merchant_id=1)
    )

    assert result.allowed is True
    assert result.role == "MANAGER"


async def test_verify_access_denies_non_member():
    merchant = make_merchant(id_=1)
    uow = FakeUnitOfWork(merchants=[merchant])

    result = await VerifyAccessUseCase(uow)(
        VerifyAccessDTO(user_id="stranger", merchant_id=1)
    )

    assert result.allowed is False


async def test_verify_access_denies_inactive_member():
    merchant = make_merchant(id_=1)
    member = make_member(merchant_id=1, user_id="user-1", is_active=False)
    uow = FakeUnitOfWork(merchants=[merchant], members=[member])

    result = await VerifyAccessUseCase(uow)(
        VerifyAccessDTO(user_id="user-1", merchant_id=1)
    )

    assert result.allowed is False


async def test_verify_access_denies_pending_merchant():
    merchant = make_merchant(id_=1, status="PENDING_VERIFICATION")
    member = make_member(merchant_id=1, user_id="user-1")
    uow = FakeUnitOfWork(merchants=[merchant], members=[member])

    result = await VerifyAccessUseCase(uow)(
        VerifyAccessDTO(user_id="user-1", merchant_id=1)
    )

    assert result.allowed is False
