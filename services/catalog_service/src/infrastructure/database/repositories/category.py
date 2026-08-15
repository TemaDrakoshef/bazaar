from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree

from src.infrastructure.database.models.category import (
    CategoryORM,
)
from src.infrastructure.database.repositories.base import (
    BaseRepository,
)


class CategoryRepository(BaseRepository):
    """Repository for managing Category entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the CategoryRepository with a database session."""

        super().__init__(session=session, model=CategoryORM)

    async def get_descendants(self, path: str) -> list[CategoryORM]:
        """Retrieves every category whose path lies under ``path``, including itself."""

        query = select(self._model).where(
            self._model.path.descendant_of(Ltree(path))
        )
        result = await self._session.execute(query)
        return result.scalars().all()
