from src.domain.entities.media import ProductMedia
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
            result = Product.model_validate(product)
            media = await uow.media.list_by_product(product_id)
            result.media = [ProductMedia.model_validate(item) for item in media]
            return result
