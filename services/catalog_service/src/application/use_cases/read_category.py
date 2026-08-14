from src.domain.entities.category import Category
from src.domain.exceptions import CategoryNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ReadCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self, category_id: int) -> Category:
        async with self.uow as uow:
            category = await uow.category.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundError()
            return Category(
                id=category.id,
                name=category.name,
                path=str(category.path),
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
