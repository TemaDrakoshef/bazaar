import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MediaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEDIA_TYPE_UNSPECIFIED: _ClassVar[MediaType]
    MEDIA_TYPE_IMAGE: _ClassVar[MediaType]
    MEDIA_TYPE_VIDEO: _ClassVar[MediaType]
MEDIA_TYPE_UNSPECIFIED: MediaType
MEDIA_TYPE_IMAGE: MediaType
MEDIA_TYPE_VIDEO: MediaType

class ProductIdRequest(_message.Message):
    __slots__ = ("product_id",)
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    def __init__(self, product_id: _Optional[int] = ...) -> None: ...

class CategoryIdRequest(_message.Message):
    __slots__ = ("category_id",)
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    def __init__(self, category_id: _Optional[int] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "category_id", "title", "description", "price", "stock", "is_active", "created_at", "updated_at", "merchant_id", "media")
    ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    id: int
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    merchant_id: int
    media: _containers.RepeatedCompositeFieldContainer[ProductMedia]
    def __init__(self, id: _Optional[int] = ..., category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., merchant_id: _Optional[int] = ..., media: _Optional[_Iterable[_Union[ProductMedia, _Mapping]]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("category_id", "title", "description", "price", "stock", "merchant_id")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    merchant_id: int
    def __init__(self, category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ..., merchant_id: _Optional[int] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ("limit", "offset", "merchant_id")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    merchant_id: int
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ..., merchant_id: _Optional[int] = ...) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products", "count")
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    count: int
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("product_id", "category_id", "title", "description", "price", "stock", "is_active", "merchant_id")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    is_active: bool
    merchant_id: int
    def __init__(self, product_id: _Optional[int] = ..., category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ..., is_active: _Optional[bool] = ..., merchant_id: _Optional[int] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("product_id", "merchant_id")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    merchant_id: int
    def __init__(self, product_id: _Optional[int] = ..., merchant_id: _Optional[int] = ...) -> None: ...

class Category(_message.Message):
    __slots__ = ("id", "name", "path", "is_active", "created_at", "updated_at", "parent_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    path: str
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    parent_id: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., path: _Optional[str] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parent_id: _Optional[int] = ...) -> None: ...

class CreateCategoryRequest(_message.Message):
    __slots__ = ("name", "parent_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    parent_id: int
    def __init__(self, name: _Optional[str] = ..., parent_id: _Optional[int] = ...) -> None: ...

class ListCategoriesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCategoriesResponse(_message.Message):
    __slots__ = ("categories",)
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[Category]
    def __init__(self, categories: _Optional[_Iterable[_Union[Category, _Mapping]]] = ...) -> None: ...

class UpdateCategoryRequest(_message.Message):
    __slots__ = ("category_id", "name", "is_active")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    name: str
    is_active: bool
    def __init__(self, category_id: _Optional[int] = ..., name: _Optional[str] = ..., is_active: _Optional[bool] = ...) -> None: ...

class MoveCategoryRequest(_message.Message):
    __slots__ = ("category_id", "parent_id")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    parent_id: int
    def __init__(self, category_id: _Optional[int] = ..., parent_id: _Optional[int] = ...) -> None: ...

class ProductMedia(_message.Message):
    __slots__ = ("id", "product_id", "media_type", "url", "position", "width", "height", "duration_seconds", "file_size")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    id: int
    product_id: int
    media_type: MediaType
    url: str
    position: int
    width: int
    height: int
    duration_seconds: int
    file_size: int
    def __init__(self, id: _Optional[int] = ..., product_id: _Optional[int] = ..., media_type: _Optional[_Union[MediaType, str]] = ..., url: _Optional[str] = ..., position: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., duration_seconds: _Optional[int] = ..., file_size: _Optional[int] = ...) -> None: ...

class GetMediaUploadUrlRequest(_message.Message):
    __slots__ = ("product_id", "merchant_id", "media_type", "content_type", "file_size")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    merchant_id: int
    media_type: MediaType
    content_type: str
    file_size: int
    def __init__(self, product_id: _Optional[int] = ..., merchant_id: _Optional[int] = ..., media_type: _Optional[_Union[MediaType, str]] = ..., content_type: _Optional[str] = ..., file_size: _Optional[int] = ...) -> None: ...

class GetMediaUploadUrlResponse(_message.Message):
    __slots__ = ("upload_url", "storage_key", "public_url")
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    storage_key: str
    public_url: str
    def __init__(self, upload_url: _Optional[str] = ..., storage_key: _Optional[str] = ..., public_url: _Optional[str] = ...) -> None: ...

class ConfirmMediaUploadRequest(_message.Message):
    __slots__ = ("product_id", "merchant_id", "media_type", "storage_key", "public_url", "file_size", "width", "height", "duration_seconds")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    merchant_id: int
    media_type: MediaType
    storage_key: str
    public_url: str
    file_size: int
    width: int
    height: int
    duration_seconds: int
    def __init__(self, product_id: _Optional[int] = ..., merchant_id: _Optional[int] = ..., media_type: _Optional[_Union[MediaType, str]] = ..., storage_key: _Optional[str] = ..., public_url: _Optional[str] = ..., file_size: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., duration_seconds: _Optional[int] = ...) -> None: ...

class DeleteMediaRequest(_message.Message):
    __slots__ = ("product_id", "merchant_id", "media_id")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    merchant_id: int
    media_id: int
    def __init__(self, product_id: _Optional[int] = ..., merchant_id: _Optional[int] = ..., media_id: _Optional[int] = ...) -> None: ...

class ReorderMediaItem(_message.Message):
    __slots__ = ("media_id", "position")
    MEDIA_ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    media_id: int
    position: int
    def __init__(self, media_id: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...

class ReorderMediaRequest(_message.Message):
    __slots__ = ("product_id", "merchant_id", "items")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    merchant_id: int
    items: _containers.RepeatedCompositeFieldContainer[ReorderMediaItem]
    def __init__(self, product_id: _Optional[int] = ..., merchant_id: _Optional[int] = ..., items: _Optional[_Iterable[_Union[ReorderMediaItem, _Mapping]]] = ...) -> None: ...
