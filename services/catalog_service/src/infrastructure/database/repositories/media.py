from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.media import (
    ProductMediaORM,
)
from src.infrastructure.database.repositories.base import (
    BaseRepository,
)


class MediaRepository(BaseRepository):
    """Repository for managing ProductMedia entities in the database."""

    def __init__(self, session: AsyncSession):
        """Initializes the MediaRepository with a database session."""

        super().__init__(session=session, model=ProductMediaORM)

    async def list_by_product(self, product_id: int) -> list[ProductMediaORM]:
        """Returns media of one product ordered by position and id."""
        query = (
            select(ProductMediaORM)
            .where(ProductMediaORM.product_id == product_id)
            .order_by(ProductMediaORM.position.asc(), ProductMediaORM.id.asc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def list_by_products(
        self, product_ids: list[int]
    ) -> dict[int, list[ProductMediaORM]]:
        """Batch-loads media for many products, grouped by product_id."""
        if not product_ids:
            return {}
        query = (
            select(ProductMediaORM)
            .where(ProductMediaORM.product_id.in_(product_ids))
            .order_by(ProductMediaORM.position.asc(), ProductMediaORM.id.asc())
        )
        result = await self._session.execute(query)
        grouped: dict[int, list[ProductMediaORM]] = {}
        for record in result.scalars().all():
            grouped.setdefault(record.product_id, []).append(record)
        return grouped

    async def list_by_ids(self, media_ids: list[int]) -> list[ProductMediaORM]:
        """Returns media records matching the given ids."""
        if not media_ids:
            return []
        query = select(ProductMediaORM).where(ProductMediaORM.id.in_(media_ids))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def next_position(self, product_id: int) -> int:
        """Returns the next position value (max(position) + 1)."""
        query = select(func.max(ProductMediaORM.position)).where(
            ProductMediaORM.product_id == product_id
        )
        result = await self._session.execute(query)
        current = result.scalar_one()
        return (current if current is not None else -1) + 1

    async def has_video(self, product_id: int) -> bool:
        """Returns True when the product already has a video."""
        query = (
            select(ProductMediaORM.id)
            .where(
                ProductMediaORM.product_id == product_id,
                ProductMediaORM.media_type == "VIDEO",
            )
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalars().first() is not None

    async def update_positions(self, updates: list[tuple[int, int]]) -> None:
        """Batch-updates ``position`` for the given ``(media_id, position)`` pairs."""
        for media_id, position in updates:
            query = (
                update(ProductMediaORM)
                .where(ProductMediaORM.id == media_id)
                .values(position=position)
            )
            await self._session.execute(query)
