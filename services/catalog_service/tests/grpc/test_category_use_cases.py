"""Unit tests for category use cases against an in-memory fake unit of work."""

from __future__ import annotations

import pytest

from src.application.use_cases.create_category import CreateCategoryUseCase
from src.application.use_cases.delete_category import DeleteCategoryUseCase
from src.application.use_cases.move_category import MoveCategoryUseCase
from src.domain.dtos.category import CategoryCreateDTO, CategoryMoveDTO
from src.domain.exceptions import (
    CategoryHasChildrenError,
    CategoryHasProductsError,
    CategoryMoveError,
    CategoryNotFoundError,
)
from tests.conftest import FakeUnitOfWork, make_category, make_product

pytestmark = pytest.mark.unit


def _tree() -> list:
    return [
        make_category(id_=1, path="1", parent_id=None),
        make_category(id_=7, path="7", parent_id=None),
        make_category(id_=2, path="1.2", parent_id=1),
        make_category(id_=3, path="1.2.3", parent_id=2),
        make_category(id_=4, path="1.2.4", parent_id=2),
        make_category(id_=5, path="1.2.3.5", parent_id=3),
    ]


async def test_create_root_category():
    uow = FakeUnitOfWork()
    result = await CreateCategoryUseCase(uow)(CategoryCreateDTO(name="root"))

    assert result.parent_id is None
    assert result.path == str(result.id)


async def test_create_child_under_parent():
    root = make_category(id_=1, path="1", parent_id=None)
    uow = FakeUnitOfWork(categories=[root])

    result = await CreateCategoryUseCase(uow)(
        CategoryCreateDTO(name="child", parent_id=1)
    )

    assert result.parent_id == 1
    assert result.path == f"1.{result.id}"


async def test_move_rewrites_descendant_paths():
    uow = FakeUnitOfWork(categories=_tree())

    result = await MoveCategoryUseCase(uow)(
        2, CategoryMoveDTO(parent_id=7)
    )

    assert result.path == "7.2"
    assert result.parent_id == 7
    by_id = {c.id: c for c in uow.category.records}
    assert by_id[3].path == "7.2.3"
    assert by_id[4].path == "7.2.4"
    assert by_id[5].path == "7.2.3.5"
    assert by_id[3].parent_id == 2
    assert by_id[4].parent_id == 2
    assert by_id[5].parent_id == 3


async def test_move_under_descendant_rejected():
    uow = FakeUnitOfWork(categories=_tree())

    with pytest.raises(CategoryMoveError):
        await MoveCategoryUseCase(uow)(1, CategoryMoveDTO(parent_id=4))


async def test_move_into_itself_rejected():
    uow = FakeUnitOfWork(categories=_tree())

    with pytest.raises(CategoryMoveError):
        await MoveCategoryUseCase(uow)(2, CategoryMoveDTO(parent_id=2))


async def test_move_unknown_category_not_found():
    uow = FakeUnitOfWork(categories=_tree())

    with pytest.raises(CategoryNotFoundError):
        await MoveCategoryUseCase(uow)(999, CategoryMoveDTO(parent_id=7))


async def test_move_unknown_parent_not_found():
    uow = FakeUnitOfWork(categories=_tree())

    with pytest.raises(CategoryNotFoundError):
        await MoveCategoryUseCase(uow)(2, CategoryMoveDTO(parent_id=999))


async def test_move_to_root():
    uow = FakeUnitOfWork(categories=_tree())

    result = await MoveCategoryUseCase(uow)(2, CategoryMoveDTO(parent_id=None))

    assert result.parent_id is None
    assert result.path == "2"


async def test_delete_category_with_children_rejected():
    uow = FakeUnitOfWork(categories=_tree())

    with pytest.raises(CategoryHasChildrenError):
        await DeleteCategoryUseCase(uow)(1)


async def test_delete_category_with_products_rejected():
    category = make_category(id_=1, path="1", parent_id=None)
    product = make_product(id_=1, category_id=1)
    uow = FakeUnitOfWork(categories=[category], products=[product])

    with pytest.raises(CategoryHasProductsError):
        await DeleteCategoryUseCase(uow)(1)


async def test_delete_empty_category_succeeds():
    category = make_category(id_=1, path="1", parent_id=None)
    uow = FakeUnitOfWork(categories=[category])

    await DeleteCategoryUseCase(uow)(1)

    assert uow.category.records == []
