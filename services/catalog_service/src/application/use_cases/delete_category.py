import structlog

from src.domain.exceptions import CategoryNotFoundError
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

            await uow.category.delete(category_id)
            await uow.commit()

        logger.info("category.deleted", category_id=category_id)
