from src.domain.dtos.category import CategoryCreateDTO
from src.domain.entities.category import Category
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, data: CategoryCreateDTO) -> Category:
        """Create a new category."""
        async with self._uow as uow:
            uow: SQLAlchemyUnitOfWork

            new_category = Category(name=data.name, path="temp")
            uow._session.add(new_category)
            await uow._session.flush()

            if not data.parent_id:
                new_category.path = str(new_category.id)
            else:
                parent_category = await uow.category.get_by_id(data.parent_id)
                if not parent_category:
                    raise ValueError(
                        f"Parent category with ID {data.parent_id} not found."
                    )

                new_category.path = f"{parent_category.path}.{new_category.id}"

            await uow.commit()

            refreshed = await uow.category.get_by_id(new_category.id)
            response = Category.model_validate(refreshed)
        return response
