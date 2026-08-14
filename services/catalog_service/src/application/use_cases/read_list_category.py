from src.domain.entities.category import Category
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork


class ReadListCategoriesUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def __call__(self) -> list[Category]:
        async with self.uow as uow:
            categories = await uow.category.get_all_by_filter()
            return [
                Category(
                    id=category.id,
                    name=category.name,
                    path=str(category.path),
                    is_active=category.is_active,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                )
                for category in categories
            ]
