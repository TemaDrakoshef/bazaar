from src.domain.entities.product import Product
from src.domain.exceptions import ProductNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ReadProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, product_id: int) -> Product:
        async with self.uow as uow:
            product = await uow.product.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError()
            return Product.model_validate(product)
