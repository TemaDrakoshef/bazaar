from abc import ABC, abstractmethod

from src.domain.dtos.catalog import CategoryCreateDTO, CategoryResult


class AbstractCatalogGateway(ABC):
    """Port for every catalog operation the gateway performs."""

    @abstractmethod
    async def create_category(self, data: CategoryCreateDTO) -> CategoryResult: ...
