import uuid
from abc import ABC, abstractmethod


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
