from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.product import ProductORM
from src.persistence.repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for managing Product entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the ProductRepository with a database session."""

        super().__init__(session=session, model=ProductORM)
