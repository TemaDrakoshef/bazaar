import structlog

from src.domain.exceptions import ProductNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class DeleteProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, product_id: int) -> None:
        async with self.uow as uow:
            existing = await uow.product.get_by_id(product_id)
            if not existing:
                raise ProductNotFoundError(str(product_id))

            await uow.product.delete(product_id)
            await uow.commit()

        logger.info("product.deleted", product_id=product_id)
