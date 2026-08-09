from sqlalchemy.ext.asyncio import AsyncSession

from services.catalog_service.src.infrastructure.database.models.category import (
    CategoryORM,
)
from services.catalog_service.src.infrastructure.database.repositories.base import (
    BaseRepository,
)


class CategoryRepository(BaseRepository):
    """Repository for managing Category entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the CategoryRepository with a database session."""

        super().__init__(session=session, model=CategoryORM)
