from src.domain.dtos.product import ProductUpdateDTO
from src.domain.entities.product import Product
from src.domain.exceptions import CategoryNotFoundError, ProductNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


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
                return Product.model_validate(existing)

            updated = await uow.product.update(product_id, **values)
            await uow.commit()

            refreshed = await uow.product.get_by_id(product_id)
            return Product.model_validate(refreshed or updated)
