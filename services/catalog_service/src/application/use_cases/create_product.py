from src.domain.dtos.product import ProductCreateDTO
from src.domain.entities.product import Product
from src.domain.exceptions import CategoryNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class CreateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, data: ProductCreateDTO) -> Product:
        """Create a new product."""
        async with self._uow as uow:
            category = await uow.category.get_by_id(data.category_id)
            if not category:
                raise CategoryNotFoundError(str(data.category_id))

            values = data.model_dump()
            product = await uow.product.create(**values)
            await uow.commit()

            refreshed = await uow.product.get_by_id(product.id)
            response = Product.model_validate(refreshed)

        return response
