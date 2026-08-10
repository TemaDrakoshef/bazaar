from sqlalchemy_utils import Ltree

from src.domain.dtos.category import CategoryCreateDTO
from src.domain.entities.category import Category
from src.domain.exceptions import CategoryNotFoundError
from src.domain.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, data: CategoryCreateDTO) -> Category:
        """Create a new category."""
        async with self._uow as uow:
            uow: SQLAlchemyUnitOfWork

            new_category = await uow.category.create(
                name=data.name,
                path=Ltree("temp"),
            )

            if not data.parent_id:
                new_path = Ltree(str(new_category.id))
            else:
                parent_category = await uow.category.get_by_id(data.parent_id)
                if not parent_category:
                    raise CategoryNotFoundError(str(data.parent_id))

                new_path = Ltree(f"{parent_category.path}.{new_category.id}")

            await uow.category.update(new_category.id, path=new_path)
            await uow.commit()

            refreshed = await uow.category.get_by_id(new_category.id)
            response = Category(
                id=refreshed.id,
                name=refreshed.name,
                path=str(refreshed.path),
                is_active=refreshed.is_active,
                created_at=refreshed.created_at,
                updated_at=refreshed.updated_at,
            )

        return response
