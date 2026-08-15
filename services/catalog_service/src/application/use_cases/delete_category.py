import structlog

from src.domain.exceptions import (
    CategoryHasChildrenError,
    CategoryHasProductsError,
    CategoryNotFoundError,
)
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class DeleteCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, category_id: int) -> None:
        async with self.uow as uow:
            existing = await uow.category.get_by_id(category_id)
            if not existing:
                raise CategoryNotFoundError(str(category_id))

            children = await uow.category.get_all_by_filter(parent_id=category_id)
            if children:
                raise CategoryHasChildrenError()

            product_count = await uow.product.count(category_id=category_id)
            if product_count:
                raise CategoryHasProductsError()

            await uow.category.delete(category_id)
            await uow.commit()

        logger.info("category.deleted", category_id=category_id)
