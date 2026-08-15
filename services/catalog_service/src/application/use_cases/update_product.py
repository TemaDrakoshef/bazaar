import structlog

from src.domain.dtos.product import ProductUpdateDTO
from src.domain.entities.product import Product
from src.domain.exceptions import CategoryNotFoundError, ProductNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork

logger = structlog.get_logger()


class UpdateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, product_id: int, data: ProductUpdateDTO) -> Product:
        async with self.uow as uow:
            existing = await uow.product.get_by_id(product_id)
            if not existing:
                raise ProductNotFoundError(str(product_id))

            if data.category_id is not None:
                category = await uow.category.get_by_id(data.category_id)
                if not category:
                    raise CategoryNotFoundError(str(data.category_id))

            values = data.model_dump(exclude_none=True)
            if not values:
                await uow.commit()
                logger.info("product.updated", product_id=product_id, no_changes=True)
                return Product.model_validate(existing)

            updated = await uow.product.update(product_id, **values)
            await uow.commit()

            refreshed = await uow.product.get_by_id(product_id)
            result = Product.model_validate(refreshed or updated)

        logger.info("product.updated", product_id=result.id, fields=list(values))
        return result
