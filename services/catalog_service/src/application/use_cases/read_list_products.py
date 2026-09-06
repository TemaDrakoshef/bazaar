from src.domain.dtos.product import ProductListQueryDTO
from src.domain.entities.media import ProductMedia
from src.domain.entities.product import Product
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ReadListProductsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, query: ProductListQueryDTO) -> tuple[list[Product], int]:
        filters: dict[str, int] = {}
        if query.merchant_id is not None:
            filters["merchant_id"] = query.merchant_id

        async with self.uow as uow:
            products = await uow.product.get_page(
                offset=query.offset, limit=query.limit, **filters
            )
            count = await uow.product.count(**filters)
            media_by_product = await uow.media.list_by_products(
                [product.id for product in products]
            )
            result = []
            for product in products:
                item = Product.model_validate(product)
                item.media = [
                    ProductMedia.model_validate(media)
                    for media in media_by_product.get(product.id, [])
                ]
                result.append(item)
            return result, count
