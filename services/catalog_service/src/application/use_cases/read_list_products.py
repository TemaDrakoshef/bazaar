from src.domain.dtos.product import ProductListQueryDTO
from src.domain.entities.product import Product
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ReadListProductsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, query: ProductListQueryDTO) -> tuple[list[Product], int]:
        async with self.uow as uow:
            products = await uow.product.get_page(
                offset=query.offset, limit=query.limit
            )
            count = await uow.product.count()
            return [Product.model_validate(product) for product in products], count
