import structlog

from src.domain.dtos.category import CategoryUpdateDTO
from src.domain.entities.category import Category
from src.domain.exceptions import CategoryNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class UpdateCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, category_id: int, data: CategoryUpdateDTO) -> Category:
        async with self.uow as uow:
            existing = await uow.category.get_by_id(category_id)
            if not existing:
                raise CategoryNotFoundError(str(category_id))

            values = data.model_dump(exclude_none=True)

            if not values:
                await uow.commit()
                logger.info(
                    "category.updated", category_id=category_id, no_changes=True
                )
                return Category(
                    id=existing.id,
                    name=existing.name,
                    parent_id=existing.parent_id,
                    path=str(existing.path),
                    is_active=existing.is_active,
                    created_at=existing.created_at,
                    updated_at=existing.updated_at,
                )

            await uow.category.update(category_id, **values)
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

        logger.info("category.updated", category_id=result.id, fields=list(values))
        return result
