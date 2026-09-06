from abc import ABC, abstractmethod

from src.domain.dtos.catalog import (
    CategoryCreateDTO,
    CategoryListQuery,
    CategoryMoveDTO,
    CategoryResult,
    CategoryUpdateDTO,
    ConfirmMediaUploadInput,
    DeleteMediaInput,
    MediaUploadUrlInput,
    MediaUploadUrlResult,
    ProductCreateDTO,
    ProductListQuery,
    ProductListResult,
    ProductMediaResult,
    ProductResult,
    ProductUpdateDTO,
    ReorderMediaInput,
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
        self, merchant_id: int, product_id: int, data: ProductUpdateDTO
    ) -> ProductResult: ...

    @abstractmethod
    async def delete_product(self, merchant_id: int, product_id: int) -> None: ...

    @abstractmethod
    async def get_media_upload_url(
        self, data: MediaUploadUrlInput
    ) -> MediaUploadUrlResult: ...

    @abstractmethod
    async def confirm_media_upload(
        self, data: ConfirmMediaUploadInput
    ) -> ProductMediaResult: ...

    @abstractmethod
    async def delete_media(self, data: DeleteMediaInput) -> None: ...

    @abstractmethod
    async def reorder_media(self, data: ReorderMediaInput) -> None: ...
