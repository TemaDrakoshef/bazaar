from abc import ABC, abstractmethod

from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryMoveDTO,
    CategoryResult,
    CategoryUpdateDTO,
    ProductCreateDTO,
    ProductListQuery,
    ProductListResult,
    ProductResult,
    ProductUpdateDTO,
)


class AbstractCatalogGateway(ABC):
    """Port for every catalog operation the gateway performs."""

    @abstractmethod
    async def create_category(self, data: CategoryCreateDTO) -> CategoryResult: ...

    @abstractmethod
    async def read_category(self, category_id: int) -> CategoryResult: ...

    @abstractmethod
    async def read_list_categories(
        self, query: CategoryListQuery
    ) -> list[CategoryResult]: ...

    @abstractmethod
    async def update_category(
        self, category_id: int, data: CategoryUpdateDTO
    ) -> CategoryResult: ...

    @abstractmethod
    async def delete_category(self, category_id: int) -> None: ...

    @abstractmethod
    async def move_category(
        self, category_id: int, data: CategoryMoveDTO
    ) -> CategoryResult: ...

    @abstractmethod
    async def create_product(self, data: ProductCreateDTO) -> ProductResult: ...

    @abstractmethod
    async def read_product(self, product_id: int) -> ProductResult: ...

    @abstractmethod
    async def read_list_products(
        self, query: ProductListQuery
    ) -> ProductListResult: ...

    @abstractmethod
    async def update_product(
        self, product_id: int, data: ProductUpdateDTO
    ) -> ProductResult: ...

    @abstractmethod
    async def delete_product(self, product_id: int) -> None: ...
