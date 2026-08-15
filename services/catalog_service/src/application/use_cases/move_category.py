import structlog
from sqlalchemy_utils import Ltree

from src.domain.dtos.category import CategoryMoveDTO
from src.domain.entities.category import Category
from src.domain.exceptions import (
    CategoryMoveError,
    CategoryNotFoundError,
)
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


def is_self_or_descendant(category_path: str, candidate_path: str) -> bool:
    """Return True when ``candidate_path`` is the same node or lies under it."""
    return candidate_path == category_path or candidate_path.startswith(
        f"{category_path}."
    )


class MoveCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, category_id: int, data: CategoryMoveDTO) -> Category:
        async with self.uow as uow:
            category = await uow.category.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundError(str(category_id))

            old_path = str(category.path)
            new_parent_id = data.parent_id

            if new_parent_id is not None:
                new_parent = await uow.category.get_by_id(new_parent_id)
                if not new_parent:
                    raise CategoryNotFoundError(str(new_parent_id))
                if is_self_or_descendant(old_path, str(new_parent.path)):
                    raise CategoryMoveError(str(category_id))
                new_path = f"{new_parent.path}.{category_id}"
            else:
                new_path = str(category_id)

            descendants = await uow.category.get_descendants(old_path)

            await uow.category.update(
                category_id, path=Ltree(new_path), parent_id=new_parent_id
            )

            old_prefix = f"{old_path}."
            for descendant in descendants:
                if descendant.id == category_id:
                    continue
                rest = str(descendant.path)[len(old_prefix) :]
                descendant_path = f"{new_path}.{rest}"
                parts = rest.split(".")
                if len(parts) == 1:
                    parent_id_value = category_id
                else:
                    parent_id_value = int(parts[-2])
                await uow.category.update(
                    descendant.id,
                    path=Ltree(descendant_path),
                    parent_id=parent_id_value,
                )

            await uow.commit()

            refreshed = await uow.category.get_by_id(category_id)
            result = Category(
                id=refreshed.id,
                name=refreshed.name,
                parent_id=refreshed.parent_id,
                path=str(refreshed.path),
                is_active=refreshed.is_active,
                created_at=refreshed.created_at,
                updated_at=refreshed.updated_at,
            )

        logger.info(
            "category.moved",
            category_id=category_id,
            parent_id=new_parent_id,
            path=result.path,
        )
        return result
