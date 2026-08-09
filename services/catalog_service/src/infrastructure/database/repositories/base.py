import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AbstractBaseRepository(ABC):
    """Abstract base class for repository implementations."""

    @abstractmethod
    async def create(self, **values):
        """Creates a new entity in the database with the provided values."""
        pass

    @abstractmethod
    async def get_by_id(self, id_: uuid.UUID):
        """Retrieves an entity by its ID."""
        pass

    @abstractmethod
    async def get_one_or_none(self, **filters):
        """
        Retrieves a single entity matching the provided filters, or None if not found.
        """
        pass

    @abstractmethod
    async def get_all_by_filter(self, **filters):
        """Retrieves all entities matching the provided filters."""
        pass

    @abstractmethod
    async def delete(self, id_: uuid.UUID):
        """Deletes an entity by its ID."""
        pass

    @abstractmethod
    async def update(self, id_: uuid.UUID, **values):
        """Updates an entity by its ID with the provided values."""
        pass


class BaseRepository(AbstractBaseRepository):
    """Base class for repository implementations."""

    def __init__(self, session: AsyncSession, model: type[T]):
        """Initializes the BaseRepository with a database session and model class."""

        self._session = session
        self._model = model

    async def create(self, **values):
        """Creates a new entity in the database with the provided values."""

        query = insert(self._model).values(**values).returning(self._model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, id_: uuid.UUID):
        """Retrieves an entity by its ID."""

        query = select(self._model).where(self._model.id == id_)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_one_or_none(self, **filters):
        """
        Retrieves a single entity matching the provided filters, or None if not found.
        """

        query = select(self._model).filter_by(**filters)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_all_by_filter(self, **filters):
        """Retrieves all entities matching the provided filters."""

        query = select(self._model).filter_by(**filters)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def delete(self, id_: uuid.UUID):
        """Deletes an entity by its ID."""

        query = delete(self._model).where(self._model.id == id_).returning(self._model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def update(self, id_: uuid.UUID, **values):
        """Updates an entity by its ID with the provided values."""

        query = (
            update(self._model)
            .where(self._model.id == id_)
            .values(**values)
            .returning(self._model)
        )
        result = await self._session.execute(query)
        return result.scalars().first()
